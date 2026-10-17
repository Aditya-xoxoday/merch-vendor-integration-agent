/** DRAFT unit tests for Printstop (see code/README.md). Fixtures: tests/vendors/fixtures/printstop*.json */
jest.mock("@plum-xoxo/correlation-logger/logger", () => ({
  logger: { info: jest.fn(), error: jest.fn(), warn: jest.fn(), debug: jest.fn() },
}));
jest.mock("@utils/db");

import Printstop from "@vendors/integratedVendors/Printstop";
import order from "./fixtures/printstopOrder.json";
import duplicate from "./fixtures/printstopOrderDuplicate.json";
import status from "./fixtures/printstopStatusInProduction.json";
import details from "./fixtures/printstopProductDetails.json";

const config = { // VERIFY: shape the base constructor expects
  vendorData: { vendorId: 0, name: "Printstop", model: "printstop_merchandise", merchandiseVendor: true },
  configs: {
    baseUrl: "https://www.psstaging.in", cdnUrl: "https://cdn.example",
    credentials: { printstop: { clientId: "x", clientSecret: "y", userName: "z", corporateId: "195",
      companyName: "Acme", corporateBillingId: "1219", orderEmail: "orders@example.com" } },
  },
  webhookConfigs: { orderStatus: { "in production": "CONFIRMED" } },
};
const vendor = () => new (Printstop as any)(config);
const data = {
  shipping_firstname: "Asha", shipping_lastname: "", shipping_address_1: "1 Road", shipping_address_2: "",
  shipping_city: "Mumbai", shipping_zone: "Maharashtra", shipping_country: "IN", shipping_postcode: 400001,
  shipping_contact_no: "+91 98765 43210", externalOrderId: "555", api_product_name: "8093_14513",
};

describe("formatOrderResponse", () => {
  it("builds code, apiOrderId and addedBy", () => {
    expect(vendor().formatOrderResponse(order, data)).toEqual({
      code: "printstop_merchandise_vendor_6777648", pin: "", validity: "",
      apiOrderId: "6777648", addedBy: "Printstop API",
    });
  });
  it("throws the raw response when orders_id is missing", () => {
    expect(() => vendor().formatOrderResponse({ success: "true" }, data)).toThrow();
  });
});

describe("getPlaceOrderReqOptions", () => {
  it("maps profile, product and shipping", async () => {
    const { body } = await vendor().getPlaceOrderReqOptions(data);
    expect(body.profile).toMatchObject({ first_name: "Asha", last_name: "Asha", mobile_number: "9876543210",
      reference_number: "555", email: "orders@example.com", corporate_id: 195 });
    expect(body.product).toEqual({ product_id: 8093, size_id: 14513 });
    expect(body.shipping).toMatchObject({ pincode: "400001", country: 99, address_line_2: "" });
    expect(JSON.stringify(body)).not.toContain("clientSecret");
  });
  it("omits size_id for sku without size", async () => {
    const { body } = await vendor().getPlaceOrderReqOptions({ ...data, api_product_name: "7422" });
    expect(body.product).toEqual({ product_id: 7422 });
  });
  it("rejects non-India addresses", async () => {
    const call = vendor().getPlaceOrderReqOptions({ ...data, shipping_country: "AE" });
    await expect(call).rejects.toThrow(/not supported/);
  });
});

describe("errorHandler", () => {
  it("never auto-links a 409 (TECH_SPEC §11.2)", async () => {
    const v = vendor();
    v.callVendorRefetch = jest.fn();
    await expect(v.errorHandler({ response: { status: 409, data: duplicate } }, data)).rejects.toBeDefined();
    expect(v.callVendorRefetch).not.toHaveBeenCalled();
  });
});

describe("formatWebhookOrderStatusResponse (polling shape)", () => {
  it("maps the In Production sample", () => {
    expect(vendor().formatWebhookOrderStatusResponse(status)).toMatchObject({
      apiOrderId: "6777648", status: "In Production", statusCode: "10", trackingId: "", link: "", courier_name: "",
    });
  });
  it("returns unknown statuses raw instead of throwing", () => {
    expect(vendor().formatWebhookOrderStatusResponse({ ...status, orders_status: "Something New" }).status)
      .toBe("Something New");
  });
  it("throws only when orders_id is missing", () => {
    expect(() => vendor().formatWebhookOrderStatusResponse({ orders_status: "x" })).toThrow();
  });
  it("parses dates", () => {
    expect(Printstop.date("17 Jul, 2024")).toBe("2024-07-17");
    expect(Printstop.date("")).toBe("");
  });
});

describe("status map", () => {
  it("only uses the six delivery statuses with lowercase keys", () => {
    const allowed = ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELED", "RETURNED"];
    for (const [k, v] of Object.entries(config.webhookConfigs.orderStatus)) {
      expect(k).toBe(k.toLowerCase());
      expect(allowed).toContain(v);
    }
  });
});

describe("refetch", () => {
  it("uses api_order_id from the DB row", () => {
    expect(vendor().getRefetchOrderReqOptions({ api_order_id: "6777648" }).url).toContain("orders_id=6777648");
  });
  it("fails clearly with only externalOrderId", () => {
    expect(() => vendor().getRefetchOrderReqOptions({ externalOrderId: "555" })).toThrow(/api_order_id/);
  });
});

describe("catalogue", () => {
  it("one row per size, sku product_size, personalised image template disabled", () => {
    const rows = vendor().formatProductResponse(details.product_details);
    expect(rows[0]).toMatchObject({ sku: "8093_14513", brand: "", status: 0 }); // fixture has an image block
    expect(rows[0].image).toBe("https://cdn.example/8093_Jack-and-Jones-Jacquard-Polo_Olive.jpg");
  });
  it("throws when listing total does not match items", async () => {
    const v = vendor();
    v.post = jest.fn().mockResolvedValue({ total: 5, data: [{ product_id: 1 }] });
    await expect(v.getVendorProducts()).rejects.toThrow(/total/);
  });
  it("throws when any details call fails", async () => {
    const v = vendor();
    v.post = jest.fn()
      .mockResolvedValueOnce({ total: 2, data: [{ product_id: 1 }, { product_id: 2 }] })
      .mockResolvedValueOnce({ product_details: { product_id: 1 } })
      .mockResolvedValueOnce({ success: false });
    await expect(v.getVendorProducts()).rejects.toThrow(/product_details/);
  });
});
