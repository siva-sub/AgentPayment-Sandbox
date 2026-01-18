/**
 * API service for interacting with APS backend mock servers.
 * 
 * In demo mode (GitHub Pages), returns mock data.
 * In local mode, connects to the backend at localhost:8080.
 */

// Detect if running on GitHub Pages (static hosting without backend)
export const IS_DEMO_MODE = window.location.hostname.includes('github.io') ||
    window.location.hostname.includes('pages.dev');

const API_BASE = IS_DEMO_MODE ? '' : 'http://localhost:8080';

// ============================================================================
// Types
// ============================================================================

export interface ApiResponse<T = unknown> {
    success: boolean;
    data?: T;
    error?: string;
    status?: number;
    headers?: Record<string, string>;
    isDemo?: boolean;
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
// Demo Mode Mock Data
// ============================================================================

const DEMO_DATA = {
    ucpDiscovery: {
        name: "APS Mock Flower Shop",
        version: "2026-01-11",
        payment: {
            handlers: [
                { id: "stripe", name: "Stripe" },
                { id: "paypal", name: "PayPal" }
            ]
        },
        capabilities: [{ name: "agent_checkout", version: "1.0" }],
        signing_keys: [{ kty: "EC", crv: "P-256" }]
    },
    ucpProducts: {
        products: [
            { id: "bouquet_roses", name: "Red Roses Bouquet", price_cents: 3500 },
            { id: "bouquet_tulips", name: "Spring Tulips", price_cents: 2800 },
            { id: "bouquet_mixed", name: "Mixed Flowers", price_cents: 4500 }
        ],
        count: 3
    },
    ucpSession: {
        id: "chk_demo_123",
        status: "in_progress",
        currency: "USD",
        line_items: [{ item: { id: "bouquet_roses" }, quantity: 1, price_cents: 3500 }],
        totals: [{ type: "total", display_text: "Total", amount: 3500 }]
    },
    acpDiscovery: {
        name: "APS Mock Store",
        api_version: "2026-01-16",
        payment_providers: [{ id: "stripe", name: "Stripe" }]
    },
    x402Info: {
        x402Version: 2,
        protocol: "x402",
        receiver: "0x209693Bc6afc0C5328bA36FaF03C514EF312287C"
    },
    x402PaymentRequired: {
        x402Version: 2,
        resource: { url: "/resource/premium-content", description: "Premium AI Model Access" },
        accepts: [{
            scheme: "exact",
            network: "eip155:84532",
            amount: "10000",
            asset: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
            payTo: "0x209693Bc6afc0C5328bA36FaF03C514EF312287C"
        }]
    },
    ap2AgentCard: {
        name: "APS Mock Electronics",
        version: "1.0",
        capabilities: {
            extensions: [{
                uri: "https://github.com/google-agentic-commerce/ap2",
                description: "Agent Payments Protocol"
            }]
        },
        skills: [{ id: "purchase", name: "Purchase Items" }]
    },
    ap2Products: {
        result: {
            products: [
                { id: "laptop_pro", name: "Laptop Pro", price_cents: 274890 },
                { id: "headphones", name: "Wireless Headphones", price_cents: 24990 }
            ],
            count: 2
        }
    }
};

// ============================================================================
// Generic fetch wrapper with demo mode support
// ============================================================================

async function apiRequest<T>(
    url: string,
    options: RequestInit = {}
): Promise<ApiResponse<T>> {
    // In demo mode, return mock data based on URL pattern
    if (IS_DEMO_MODE) {
        return getDemoResponse<T>(url, options);
    }

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

function getDemoResponse<T>(url: string, options: RequestInit = {}): ApiResponse<T> {
    const method = options.method || 'GET';

    // Simulate network delay
    // await new Promise(r => setTimeout(r, 300));

    // UCP endpoints
    if (url.includes('/mock/ucp/.well-known/ucp')) {
        return { success: true, data: DEMO_DATA.ucpDiscovery as T, isDemo: true };
    }
    if (url.includes('/mock/ucp/products')) {
        return { success: true, data: DEMO_DATA.ucpProducts as T, isDemo: true };
    }
    if (url.includes('/mock/ucp/checkout-sessions') && method === 'POST') {
        return { success: true, data: DEMO_DATA.ucpSession as T, status: 201, isDemo: true };
    }
    if (url.includes('/mock/ucp/checkout-sessions') && method === 'GET') {
        return { success: true, data: DEMO_DATA.ucpSession as T, isDemo: true };
    }
    if (url.includes('/complete')) {
        return { success: true, data: { ...DEMO_DATA.ucpSession, status: 'completed', order: { id: 'ord_demo', permalink_url: '#' } } as T, isDemo: true };
    }

    // ACP endpoints
    if (url.includes('/mock/acp/.well-known/checkout')) {
        return { success: true, data: DEMO_DATA.acpDiscovery as T, isDemo: true };
    }
    if (url.includes('/mock/acp/checkout_sessions')) {
        return { success: true, data: { id: 'cs_demo', status: 'not_ready_for_payment', line_items: [], totals: [] } as T, status: 201, isDemo: true };
    }

    // x402 endpoints
    if (url.includes('/mock/x402/info')) {
        return { success: true, data: DEMO_DATA.x402Info as T, isDemo: true };
    }
    if (url.includes('/mock/x402/resource')) {
        // Check if has payment header (simulated)
        if (url.includes('x_payment_header')) {
            return { success: true, data: { title: "Premium AI Model Access", content: "This is premium content..." } as T, isDemo: true };
        }
        return {
            success: false,
            status: 402,
            error: 'Payment required',
            headers: { 'X-Payment-Required': JSON.stringify(DEMO_DATA.x402PaymentRequired) },
            isDemo: true
        };
    }
    if (url.includes('/mock/x402/test/generate-payment')) {
        return { success: true, data: { x_payment_header: 'demo_payment_header_base64' } as T, isDemo: true };
    }

    // AP2 endpoints
    if (url.includes('/mock/ap2/.well-known/a2a')) {
        return { success: true, data: DEMO_DATA.ap2AgentCard as T, isDemo: true };
    }
    if (url.includes('/mock/ap2/message')) {
        return { success: true, data: DEMO_DATA.ap2Products as T, isDemo: true };
    }

    // Default: indicate this is demo mode
    return {
        success: false,
        error: 'Demo mode: Connect backend for full functionality',
        isDemo: true
    };
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
        if (IS_DEMO_MODE) {
            if (paymentHeader) {
                return { success: true, data: { title: "Premium Content", content: "Access granted!" }, isDemo: true };
            }
            return getDemoResponse(`/mock/x402/resource/${resourceId}`, {});
        }

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
            return { success: true, data: { confirmed: true, ...payload }, isDemo: IS_DEMO_MODE };
        case 5: // Payment Mandate
            return ap2Api.authorizePayment(
                payload.cart_mandate_id as string,
                payload.user_authorization as string
            );
        case 6: // Settlement (awaiting)
            return { success: true, data: { status: 'processing', ...payload }, isDemo: IS_DEMO_MODE };
        case 7: // Receipt
            return ap2Api.sendMessage('ap2/getReceipt', { receipt_id: payload.receipt_id });
        default:
            return { success: false, error: `Unknown AP2 step: ${step}` };
    }
}

// ============================================================================
// Dashboard API (for Dashboard component)
// ============================================================================

export const dashboardApi = {
    getProtocols: async (): Promise<ApiResponse<Array<{ id: string; name: string; status: string }>>> => {
        if (IS_DEMO_MODE) {
            return {
                success: true,
                data: [
                    { id: 'ucp', name: 'UCP (Stripe)', status: 'active' },
                    { id: 'acp', name: 'ACP (Shopify)', status: 'active' },
                    { id: 'x402', name: 'x402 (Coinbase)', status: 'active' },
                    { id: 'ap2', name: 'AP2 (Google)', status: 'active' },
                ],
                isDemo: true
            };
        }
        return apiRequest(`${API_BASE}/api/protocols`);
    },

    getScenarios: async (): Promise<ApiResponse<Array<{ id: string; name: string; protocol: string }>>> => {
        if (IS_DEMO_MODE) {
            return {
                success: true,
                data: [
                    { id: 'ucp_checkout', name: 'UCP Checkout Flow', protocol: 'UCP' },
                    { id: 'acp_session', name: 'ACP Session Create', protocol: 'ACP' },
                    { id: 'x402_payment', name: 'x402 Micropayment', protocol: 'x402' },
                    { id: 'ap2_purchase', name: 'AP2 Agent Purchase', protocol: 'AP2' },
                ],
                isDemo: true
            };
        }
        return apiRequest(`${API_BASE}/api/scenarios`);
    },

    getRuns: async (): Promise<ApiResponse<Array<{ id: string; status: string; timestamp: string }>>> => {
        if (IS_DEMO_MODE) {
            return {
                success: true,
                data: [
                    { id: 'run_demo_1', status: 'completed', timestamp: new Date().toISOString() },
                    { id: 'run_demo_2', status: 'completed', timestamp: new Date().toISOString() },
                ],
                isDemo: true
            };
        }
        return apiRequest(`${API_BASE}/api/runs`);
    },
};
