"""Canonical Commerce Gateway and Merchant AI Representation Package."""

from agent_ready_merchant.gateway.canonical import CanonicalCommerceGateway
from agent_ready_merchant.gateway.registry import CapabilityDefinition, CapabilityRegistry
from agent_ready_merchant.gateway.representation import (
    MerchantAIRepresentation,
    build_merchant_representation,
)
from agent_ready_merchant.gateway.schemas import (
    CalculateShippingRequest,
    CalculateShippingResponse,
    CheckInventoryRequest,
    CheckInventoryResponse,
    CreateOrderGatewayRequest,
    CreateOrderGatewayResponse,
    DiscoverProductsRequest,
    DiscoverProductsResponse,
    GatewayError,
    GatewayResponseEnvelope,
    GetPaymentStatusRequest,
    GetPaymentStatusResponse,
    GetProductRequest,
    GetProductResponse,
    GetQuoteRequest,
    GetQuoteResponse,
    RequestCheckoutRequest,
    RequestCheckoutResponse,
    StateOrientedContext,
)

__all__ = [
    "CanonicalCommerceGateway",
    "CapabilityRegistry",
    "CapabilityDefinition",
    "MerchantAIRepresentation",
    "build_merchant_representation",
    "GatewayResponseEnvelope",
    "GatewayError",
    "StateOrientedContext",
    "DiscoverProductsRequest",
    "DiscoverProductsResponse",
    "GetProductRequest",
    "GetProductResponse",
    "CheckInventoryRequest",
    "CheckInventoryResponse",
    "GetQuoteRequest",
    "GetQuoteResponse",
    "CalculateShippingRequest",
    "CalculateShippingResponse",
    "CreateOrderGatewayRequest",
    "CreateOrderGatewayResponse",
    "RequestCheckoutRequest",
    "RequestCheckoutResponse",
    "GetPaymentStatusRequest",
    "GetPaymentStatusResponse",
]
