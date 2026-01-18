/**
 * API service for interacting with APS backend mock servers.
 */

const API_BASE = 'http://localhost:8080';

// ============================================================================
// Types
// ============================================================================

export interface ApiResponse<T = unknown> {
    success: boolean;
    data?: T;
    error?: string;
    status?: number;
    headers?: Record<string, string>;
}

export interface DiscoveryProfile {
    name: string;
    version: string;
    payment?: {
        handlers: Array<{ id: string; name: string }>;
    };
    capabilities?: Array<{ name: string; version: string }>;
    signing_keys?: Array<Record<string, string>>;
}

export interface CheckoutSession {
    id: string;
    status: string;
    currency: string;
    line_items: Array<Record<string, unknown>>;
    totals: Array<{ type: string; display_text: string; amount: number }>;
    payment?: Record<string, unknown>;
    buyer?: Record<string, unknown>;
    fulfillment?: Record<string, unknown>;
    order?: { id: string; permalink_url: string };
}

// ============================================================================
// Generic fetch wrapper
// ============================================================================

async function apiRequest<T>(
    url: string,
    options: RequestInit = {}
): Promise<ApiResponse<T>> {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        const data = await response.json();

        if (!response.ok) {
            return {
                success: false,
                error: data.detail || `HTTP ${response.status}`,
                status: response.status,
            };
        }

        return {
            success: true,
            data: data as T,
            status: response.status,
            headers: Object.fromEntries(response.headers.entries()),
        };
    } catch (err) {
        return {
            success: false,
            error: err instanceof Error ? err.message : 'Network error',
        };
    }
}

// ============================================================================
// UCP Mock API
// ============================================================================

export const ucpApi = {
    discover: () =>
        apiRequest<DiscoveryProfile>(`${API_BASE}/mock/ucp/.well-known/ucp`),

    listProducts: () =>
        apiRequest<{ products: Array<Record<string, unknown>>; count: number }>(
            `${API_BASE}/mock/ucp/products`
        ),

    createCheckout: (lineItems: Array<{ item: { id: string }; quantity: number }>) =>
        apiRequest<CheckoutSession>(`${API_BASE}/mock/ucp/checkout-sessions`, {
            method: 'POST',
            body: JSON.stringify({
                currency: 'USD',
                line_items: lineItems,
            }),
        }),

    getCheckout: (id: string) =>
        apiRequest<CheckoutSession>(`${API_BASE}/mock/ucp/checkout-sessions/${id}`),

    updateCheckout: (id: string, data: Record<string, unknown>) =>
        apiRequest<CheckoutSession>(`${API_BASE}/mock/ucp/checkout-sessions/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),

    completeCheckout: (id: string, paymentData: Record<string, unknown>) =>
        apiRequest<CheckoutSession>(`${API_BASE}/mock/ucp/checkout-sessions/${id}/complete`, {
            method: 'POST',
            body: JSON.stringify({ payment_data: paymentData }),
        }),
};

// ============================================================================
// ACP Mock API
// ============================================================================

export const acpApi = {
    discover: () =>
        apiRequest<Record<string, unknown>>(`${API_BASE}/mock/acp/.well-known/checkout`),

    createSession: (items: Array<{ id: string; quantity: number }>) =>
        apiRequest<Record<string, unknown>>(`${API_BASE}/mock/acp/checkout_sessions`, {
            method: 'POST',
            body: JSON.stringify({ items }),
        }),

    getSession: (id: string) =>
        apiRequest<Record<string, unknown>>(`${API_BASE}/mock/acp/checkout_sessions/${id}`),

    updateSession: (id: string, data: Record<string, unknown>) =>
        apiRequest<Record<string, unknown>>(`${API_BASE}/mock/acp/checkout_sessions/${id}`, {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    completeSession: (id: string, paymentToken: string) =>
        apiRequest<Record<string, unknown>>(
            `${API_BASE}/mock/acp/checkout_sessions/${id}/complete`,
            {
                method: 'POST',
                body: JSON.stringify({ payment_data: { token: paymentToken } }),
            }
        ),
};

// ============================================================================
// x402 Mock API
// ============================================================================

export const x402Api = {
    getInfo: () =>
        apiRequest<Record<string, unknown>>(`${API_BASE}/mock/x402/info`),

    accessResource: async (resourceId: string, paymentHeader?: string) => {
        const headers: Record<string, string> = {};
        if (paymentHeader) {
            headers['X-PAYMENT'] = paymentHeader;
        }

        const response = await fetch(`${API_BASE}/mock/x402/resource/${resourceId}`, {
            headers,
        });

        // Handle 402 specially
        if (response.status === 402) {
            const paymentRequired = response.headers.get('X-Payment-Required');
            return {
                success: false,
                status: 402,
                error: 'Payment required',
                headers: {
                    'X-Payment-Required': paymentRequired || '',
                },
            };
        }

        const data = await response.json();
        return {
            success: response.ok,
            data,
            status: response.status,
        };
    },

    generatePayment: (resourceId: string) =>
        apiRequest<{ x_payment_header: string }>(
            `${API_BASE}/mock/x402/test/generate-payment?resource_id=${resourceId}`,
            { method: 'POST' }
        ),
};

// ============================================================================
// AP2 Mock API
// ============================================================================

export const ap2Api = {
    getAgentCard: () =>
        apiRequest<Record<string, unknown>>(`${API_BASE}/mock/ap2/.well-known/a2a`),

    sendMessage: (method: string, params: Record<string, unknown>) =>
        apiRequest<{ result?: Record<string, unknown>; error?: Record<string, unknown> }>(
            `${API_BASE}/mock/ap2/message`,
            {
                method: 'POST',
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    id: crypto.randomUUID(),
                    method,
                    params,
                }),
            }
        ),

    browseProducts: (query?: string) =>
        ap2Api.sendMessage('ap2/browseProducts', { query }),

    createCart: (items: Array<{ product_id: string; quantity: number }>) =>
        ap2Api.sendMessage('ap2/createCart', { items }),

    authorizePayment: (cartMandateId: string, userAuthorization: string) =>
        ap2Api.sendMessage('ap2/authorizePayment', {
            cart_mandate_id: cartMandateId,
            user_authorization: userAuthorization,
            payment_method: { type: 'card', token: 'tok_test' },
        }),
};

// ============================================================================
// Protocol runner - executes step against mock server
// ============================================================================

export type Protocol = 'AP2' | 'UCP' | 'ACP' | 'x402';

export async function executeProtocolStep(
    protocol: Protocol,
    step: number,
    payload: Record<string, unknown>
): Promise<ApiResponse> {
    switch (protocol) {
        case 'UCP':
            return executeUCPStep(step, payload);
        case 'ACP':
            return executeACPStep(step, payload);
        case 'x402':
            return executeX402Step(step, payload);
        case 'AP2':
            return executeAP2Step(step, payload);
        default:
            return { success: false, error: `Unknown protocol: ${protocol}` };
    }
}

async function executeUCPStep(step: number, payload: Record<string, unknown>): Promise<ApiResponse> {
    switch (step) {
        case 0: // Discovery
            return ucpApi.discover();
        case 1: // Create checkout
            return ucpApi.createCheckout(payload.line_items as any || []);
        case 2: // Update checkout
            return ucpApi.updateCheckout(payload.id as string, payload);
        case 3: // Complete
            return ucpApi.completeCheckout(payload.id as string, payload.payment_data as any || {});
        default:
            return { success: false, error: `Unknown UCP step: ${step}` };
    }
}

async function executeACPStep(step: number, payload: Record<string, unknown>): Promise<ApiResponse> {
    switch (step) {
        case 0: // Discovery
            return acpApi.discover();
        case 1: // Create session
            return acpApi.createSession(payload.items as any || []);
        case 2: // Update session
            return acpApi.updateSession(payload.id as string, payload);
        case 3: // Complete
            return acpApi.completeSession(payload.id as string, payload.token as string || '');
        default:
            return { success: false, error: `Unknown ACP step: ${step}` };
    }
}

async function executeX402Step(step: number, payload: Record<string, unknown>): Promise<ApiResponse> {
    switch (step) {
        case 0: // Info
            return x402Api.getInfo();
        case 1: // Request resource (get 402)
            return x402Api.accessResource(payload.resource_id as string || 'premium-content');
        case 2: // Generate payment
            return x402Api.generatePayment(payload.resource_id as string || 'premium-content');
        case 3: // Access with payment
            return x402Api.accessResource(
                payload.resource_id as string || 'premium-content',
                payload.x_payment_header as string
            );
        default:
            return { success: false, error: `Unknown x402 step: ${step}` };
    }
}

async function executeAP2Step(step: number, payload: Record<string, unknown>): Promise<ApiResponse> {
    switch (step) {
        case 0: // Agent Card
            return ap2Api.getAgentCard();
        case 1: // Browse products
            return ap2Api.browseProducts();
        case 2: // Intent Mandate
            return ap2Api.sendMessage('ap2/createIntentMandate', payload);
        case 3: // Cart Mandate
            return ap2Api.createCart(payload.items as any || []);
        case 4: // User Confirmation (local)
            return { success: true, data: { confirmed: true, ...payload } };
        case 5: // Payment Mandate
            return ap2Api.authorizePayment(
                payload.cart_mandate_id as string,
                payload.user_authorization as string
            );
        case 6: // Settlement (awaiting)
            return { success: true, data: { status: 'processing', ...payload } };
        case 7: // Receipt
            return ap2Api.sendMessage('ap2/getReceipt', { receipt_id: payload.receipt_id });
        default:
            return { success: false, error: `Unknown AP2 step: ${step}` };
    }
}
