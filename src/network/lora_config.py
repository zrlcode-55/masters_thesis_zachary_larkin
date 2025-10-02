"""
LoRa radio configuration parameters.

All default values are based on LoRaWAN specifications and
validated against published research.
"""

from dataclasses import dataclass
from typing import Literal

# Type definitions for LoRa parameters
SpreadingFactor = Literal[7, 8, 9, 10, 11, 12]
CodingRate = Literal[1, 2, 3, 4]  # 4/(4+CR)


@dataclass
class LoRaConfig:
    """
    LoRa physical layer configuration.
    
    References:
        [1] Semtech, "LoRa Modem Designer's Guide," AN1200.13, 2015
        [2] LoRa Alliance, "LoRaWAN 1.0.3 Specification," 2018
        [3] ETSI EN 300 220, "Short Range Devices (SRD)," v3.2.1, 2018
    """
    
    # Core LoRa parameters
    spreading_factor: SpreadingFactor = 9
    """Spreading Factor: 7 (fastest, shortest range) to 12 (slowest, longest range).
    
    Default: 9 (typical for urban deployments <5km) [Magrin+ 2017]
    """
    
    bandwidth: int = 125_000  # Hz
    """Channel bandwidth in Hz.
    
    Standard LoRaWAN values: 125 kHz (EU868, US915) or 500 kHz
    Default: 125 kHz (LoRaWAN standard) [2]
    """
    
    coding_rate: CodingRate = 1
    """Coding rate: 1 → 4/5, 2 → 4/6, 3 → 4/7, 4 → 4/8.
    
    Higher values = more error correction, longer airtime
    Default: 1 (4/5, LoRaWAN default) [2]
    """
    
    tx_power: int = 14  # dBm
    """Transmit power in dBm.
    
    Regulatory limits:
    - EU868: 14 dBm [3]
    - US915: 20-30 dBm (varies by subband)
    Default: 14 dBm (EU regulatory limit)
    """
    
    duty_cycle: float = 0.01
    """Duty cycle fraction (0.01 = 1%).
    
    Regulatory constraints (ETSI EN 300 220):
    - g1 band (868.0-868.6 MHz): 1% (36s/hour)
    - g2 band (868.7-869.2 MHz): 0.1% (3.6s/hour)
    - g3 band (869.4-869.65 MHz): 10% (360s/hour)
    
    Default: 0.01 (1%, most common) [3]
    """
    
    preamble_length: int = 8
    """Number of preamble symbols.
    
    Default: 8 (LoRaWAN standard) [2]
    """
    
    # LoRaWAN MAC parameters
    header_enabled: bool = True
    """Explicit header mode (LoRaWAN requires explicit).
    
    Default: True [2]
    """
    
    crc_enabled: bool = True
    """CRC enabled (LoRaWAN requires CRC).
    
    Default: True [2]
    """
    
    low_data_rate_optimize: bool = False
    """Low data rate optimization (automatically enabled for SF11-12).
    
    Enables mandatorily for SF ≥ 11 with BW=125kHz [1]
    Default: False (auto-enabled when needed)
    """
    
    def __post_init__(self):
        """Validate configuration parameters."""
        # Auto-enable low data rate optimization for SF 11-12
        if self.spreading_factor >= 11 and self.bandwidth == 125_000:
            object.__setattr__(self, 'low_data_rate_optimize', True)
        
        # Validate SF
        if self.spreading_factor not in range(7, 13):
            raise ValueError(f"Spreading factor must be 7-12, got {self.spreading_factor}")
        
        # Validate bandwidth
        valid_bw = [125_000, 250_000, 500_000]
        if self.bandwidth not in valid_bw:
            raise ValueError(f"Bandwidth must be one of {valid_bw}, got {self.bandwidth}")
        
        # Validate duty cycle
        if not 0 < self.duty_cycle <= 1.0:
            raise ValueError(f"Duty cycle must be in (0, 1], got {self.duty_cycle}")
        
        # Validate tx power
        if not 0 <= self.tx_power <= 30:
            raise ValueError(f"TX power must be 0-30 dBm, got {self.tx_power}")
    
    def get_required_snr(self) -> float:
        """
        Get required SNR for this spreading factor.
        
        Returns:
            Required SNR in dB for successful packet reception.
            
        Reference:
            Semtech SX1276 datasheet, Table 10
            LoRa Alliance "LoRaWAN Regional Parameters"
        """
        snr_requirements = {
            7: -7.5,
            8: -10.0,
            9: -12.5,
            10: -15.0,
            11: -17.5,
            12: -20.0
        }
        return snr_requirements[self.spreading_factor]
    
    def compute_airtime(self, payload_bytes: int) -> float:
        """
        Calculate packet airtime using Semtech formula.
        
        Args:
            payload_bytes: MAC header + application payload length in bytes
            
        Returns:
            Packet transmission time in seconds
            
        Reference:
            [1] Semtech AN1200.13, Section 4.1.1.6
            Formula: T_packet = T_preamble + T_payload
        """
        SF = self.spreading_factor
        BW = self.bandwidth
        CR = self.coding_rate
        H = 0  # Explicit header (implicit = 1)
        DE = 1 if self.low_data_rate_optimize else 0
        CRC = 1 if self.crc_enabled else 0
        
        # Symbol time [1, Eq 1]
        T_sym = (2 ** SF) / BW
        
        # Preamble time [1, Eq 2]
        T_preamble = (self.preamble_length + 4.25) * T_sym
        
        # Payload symbol count [1, Eq 3]
        numerator = 8 * payload_bytes - 4 * SF + 28 + 16 * CRC - 20 * H
        denominator = 4 * (SF - 2 * DE)
        
        n_payload = 8 + max(
            int((numerator / denominator)) * (CR + 4),
            0
        )
        
        # Payload time [1, Eq 4]
        T_payload = n_payload * T_sym
        
        # Total airtime
        T_packet = T_preamble + T_payload
        
        return T_packet
    
    def __repr__(self) -> str:
        return (
            f"LoRaConfig(SF={self.spreading_factor}, BW={self.bandwidth/1000:.0f}kHz, "
            f"CR=4/{4+self.coding_rate}, TxPower={self.tx_power}dBm, "
            f"DutyCycle={self.duty_cycle*100:.1f}%)"
        )

