/**
 * Printstop / Mandaala merchandise connector (DRAFT: see code/README.md).
 * Docs: Printstop/Mandaala API Reference (2026-10-18). Spec: tech/TECH_SPEC.md.
 * sku format: "{product_id}_{size_id}" (or "{product_id}" when the product has no sizes).
 */
import VendorMerchandiseClass from "@vendors/integratedVendors/vendorMerchandiseClass";
import { logger } from "@plum-xoxo/correlation-logger/logger";
import Helper from "@utils/helper"; // VERIFY path and export
// VERIFY: interface import paths
import { VendorBaseInterface } from "@interfaces/vendorBase";
import { VendorMerchandiseInterface } from "@interfaces/vendorMerchandise";

const API_PATH = "/services/api.php";
const TOKEN_KEY = "printstop"; // single key under configs.credentials (one fetchAccessToken call)
const INDIA_COUNTRY_CODE = 99;
const COUNTRY_CODES: Record<string, number> = { IN: INDIA_COUNTRY_CODE }; // extend only after Printstop confirms (Q6)

type Creds = {
  clientId: string; clientSecret: string; userName: string; corporateId: string;
  companyName: string; corporateBillingId: string; orderEmail: string;
};

export default class Printstop extends VendorMerchandiseClass
  implements VendorBaseInterface, VendorMerchandiseInterface {
  private get creds(): Creds {
    return this.config.configs.credentials[TOKEN_KEY];
  }

  // ---------- auth ----------

  async fetchAccessToken(credentialKey: string): Promise<string> {
    const c: Creds = this.config.configs.credentials[credentialKey];
    const res = await Helper.makeRequestWithAxios({ // VERIFY helper signature
      method: "GET",
      url: `${this.config.configs.baseUrl}${API_PATH}?method=generate_token&corporate_id=${c.corporateId}`,
      headers: { "Content-Type": "application/json", "client-secret": c.clientSecret,
        "client-id": c.clientId, "user-name": c.userName },
    });
    const token = res?.data?.access_token;
    if (!token) {
      logger.error("Printstop: generate_token returned no access_token");
      throw res?.data ?? new Error("Printstop: token missing");
    }
    return token;
  }

  async getReqHeaders(): Promise<Record<string, string>> {
    const token = await this.getAccessTokenFromDb(this.config.vendorData.vendorId, TOKEN_KEY); // VERIFY signature
    return {
      Authorization: `Bearer ${token}`,
      "client-secret": this.creds.clientSecret,
      "client-id": this.creds.clientId,
      "Content-Type": "application/json",
    };
  }

  // ---------- order ----------

  async getPlaceOrderReqOptions(data: any) {
    return {
      url: `${API_PATH}?method=order`,
      method: "POST",
      body: {
        profile: this.buildProfile(data),
        product: this.buildProduct(data),
        shipping: this.buildShipping(data),
        corporate_billing_id: Number(this.creds.corporateBillingId),
      },
    };
  }

  private buildProfile(data: any) {
    const first = String(data.shipping_firstname ?? "").trim();
    return {
      first_name: first,
      last_name: String(data.shipping_lastname ?? "").trim() || first, // required by Printstop
      email: this.creds.orderEmail, // decision D1 Model A (TECH_SPEC §5.2)
      mobile_number: Printstop.mobile(data.shipping_contact_no || data.recipientMobileNumber),
      company_name: this.creds.companyName,
      corporate_id: Number(this.creds.corporateId),
      reference_number: String(data.externalOrderId ?? data.voucherInsertId ?? ""), // VERIFY field name
      department_id: 0,
    };
  }

  private buildProduct(data: any) {
    const sku = String(data.api_product_name ?? data.sku ?? ""); // VERIFY which field carries the sku
    const [productId, sizeId] = sku.split("_");
    if (!productId || Number.isNaN(Number(productId))) {
      throw new Error(`Printstop: invalid sku "${sku}" (expected {product_id}_{size_id})`);
    }
    return sizeId ? { product_id: Number(productId), size_id: Number(sizeId) } : { product_id: Number(productId) };
  }

  private buildShipping(data: any) {
    const iso = String(data.shipping_country_iso ?? data.shipping_country ?? "IN").toUpperCase(); // VERIFY source
    const country = COUNTRY_CODES[iso] ?? (/india/i.test(iso) ? INDIA_COUNTRY_CODE : undefined);
    if (!country) {
      throw new Error(`Printstop: country "${iso}" not supported (India only until confirmed)`);
    }
    return {
      address_line_1: data.shipping_address_1,
      address_line_2: data.shipping_address_2 || "",
      city: data.shipping_city,
      state: data.shipping_zone,
      pincode: String(data.shipping_postcode ?? ""),
      country,
    };
  }

  private static mobile(raw: unknown): string {
    const digits = String(raw ?? "").replace(/\D/g, "");
    return digits.length > 10 ? digits.slice(-10) : digits; // assumption A6
  }

  formatOrderResponse(response: any, data: any) {
    const id = response?.orders_id;
    if (!id) {
      throw response;
    }
    return {
      code: `${this.config.vendorData.model}_vendor_${id}`,
      pin: "",
      validity: "",
      apiOrderId: String(id),
      addedBy: `${this.config.vendorData.name} API`, // must equal the lookup in MC validateOrder
    };
  }

  getVoucherValidity() {
    return "";
  }

  async errorHandler(error: any, data: any) {
    const status = error?.response?.status ?? error?.status;
    if (status === 409) {
      // TECH_SPEC §11.2: the 409 is keyed on the USER, not our reference. Never auto-link.
      const existing = error?.response?.data?.orders ?? [];
      logger.error(`Printstop: 409 duplicate for user; existing orders ${JSON.stringify(existing)}; manual review`);
      throw error; // VERIFY: map to an existing non-retryable OPM error id from src/utils/errors.ts
    }
    return super.errorHandler(error, data);
  }

  // ---------- status (polling) ----------

  getRefetchOrderReqOptions(row: any) {
    const apiOrderId = row?.api_order_id;
    if (!apiOrderId) {
      // Printstop cannot look up by reference_number (TECH_SPEC §11.1)
      throw new Error("Printstop: refetch needs api_order_id; lookup by externalOrderId is not supported");
    }
    return { url: `${API_PATH}?method=order_status&orders_id=${apiOrderId}`, method: "POST" };
  }

  formatWebhookOrderStatusResponse(d: any) {
    if (!d || d.orders_id === undefined || d.orders_id === null) {
      throw new Error("Printstop: status payload without orders_id");
    }
    return {
      externalOrderId: "",
      apiOrderId: String(d.orders_id),
      status: String(d.orders_status ?? ""), // base lowercases and maps; unknown → tracking only
      statusCode: String(d.orders_status_id ?? ""),
      trackingId: d.tracking_number || "",
      link: d.tracking_url || "",
      courier_name: d.shipping_company || "",
      dispatched_date: "",
      delivery_date: Printstop.date(d.actual_delivery_date),
    };
  }

  async fetchTrackingDetailsFromVendor(orders: any[]) {
    const out = [];
    for (const o of orders) {
      const res = await this.callStatus(o.api_order_id);
      out.push({
        orderProductId: o.order_product_id,
        trackingDetails: {
          trackingId: res.tracking_number || "",
          trackingUrl: res.tracking_url || "",
          courierName: res.shipping_company || "",
          estimatedDelivery: Printstop.date(res.orders_due_date),
        },
        status: res.orders_status,
      });
    }
    return out;
  }

  private async callStatus(apiOrderId: string) {
    const res = await Helper.makeRequestWithAxios({ // VERIFY helper signature
      method: "POST",
      url: `${this.config.configs.baseUrl}${API_PATH}?method=order_status&orders_id=${apiOrderId}`,
      headers: await this.getReqHeaders(),
    });
    return res.data;
  }

  /** "17 Jul, 2024" → "2024-07-17" (IST assumed, A9); "" stays "". */
  static date(raw: unknown): string {
    const m = /^(\d{1,2}) (\w{3}), (\d{4})$/.exec(String(raw ?? "").trim());
    if (!m) {
      return "";
    }
    const months = "JanFebMarAprMayJunJulAugSepOctNovDec";
    const month = months.indexOf(m[2]) / 3 + 1;
    return month > 0 ? `${m[3]}-${String(month).padStart(2, "0")}-${m[1].padStart(2, "0")}` : "";
  }

  // ---------- catalogue ----------

  async getVendorProducts() {
    const listing = await this.post("product_listing");
    const items = listing?.data ?? [];
    if (!Array.isArray(items) || items.length !== Number(listing?.total)) {
      throw new Error(`Printstop: listing total ${listing?.total} != ${items.length} items (hidden paging?)`);
    }
    const details = [];
    for (const item of items) {
      const res = await this.post("product_details", `&product_id=${item.product_id}`); // selector: A4
      if (!res?.product_details) {
        throw new Error(`Printstop: product_details failed for ${item.product_id}`); // never partial (F13)
      }
      details.push(res.product_details);
    }
    return details;
  }

  private async post(method: string, extra = "") {
    const res = await Helper.makeRequestWithAxios({ // VERIFY helper signature; it must throw on non-2xx
      method: "POST",
      url: `${this.config.configs.baseUrl}${API_PATH}?method=${method}${extra}`,
      headers: await this.getReqHeaders(),
    });
    return res.data;
  }

  formatProductResponse(p: any) {
    const needsImage = (p.templates ?? []).some((t: any) =>
      Object.keys(t).some((k) => k.endsWith("_type") && t[k] === "image"));
    const base = {
      image: String(p.product_image ?? "").replace("{cdnurl}", this.config.configs.cdnUrl ?? ""), // Q5
      description: p.product_long_des ?? "",
      categories: String(p.category_id ?? ""),
      brand: "",
      denominations: "", // fixedSku: amounts are entered in karma
      terms_conditions: "",
      how_to_use: "",
    };
    const active = p.visible === "Active" && !needsImage;
    const sizes = p.product_size ?? [];
    if (!sizes.length) {
      return [{ ...base, sku: String(p.product_id), name: p.product_name, status: active ? 1 : 0 }];
    }
    return sizes.map((s: any) => ({
      ...base,
      sku: `${p.product_id}_${s.size_id}`,
      name: `${p.product_name} - ${s.size_title}`,
      status: active && s.visible === "Active" ? 1 : 0,
    }));
  }

  formatWebhookProductResponse() {
    return { sku: "", status: 2 }; // Printstop has no product webhook
  }
}
