"""
Network simulation layer for LPWAN (LoRaWAN) behavior.

This module implements a physics-informed abstract network model
validated against published LoRaWAN research.
"""

from .lora_config import LoRaConfig
from .lpwan_network import LPWANNetwork

__all__ = ['LoRaConfig', 'LPWANNetwork']

