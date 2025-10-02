"""
Basic tests for network layer to verify cited formulas.
"""

import numpy as np
import sys
sys.path.insert(0, 'src')

from network.lora_config import LoRaConfig
from network.lpwan_network import LPWANNetwork


def test_airtime_calculation_sf9():
    """
    Test airtime calculation matches published values.
    
    Reference: Semtech AN1200.13 example calculations
    """
    config = LoRaConfig(
        spreading_factor=9,
        bandwidth=125_000,
        coding_rate=1,  # 4/5
        duty_cycle=0.01
    )
    
    # For SF=9, BW=125kHz, CR=4/5, payload=51 bytes
    # Expected: ~300-310 ms (from Semtech calculator)
    airtime = config.compute_airtime(payload_bytes=51)
    
    assert 0.300 <= airtime <= 0.320, f"Airtime {airtime:.3f}s outside expected range"
    print(f"✓ SF9 airtime: {airtime*1000:.1f} ms")


def test_collision_probability_matches_bor2016():
    """
    Test collision model matches Bor+ 2016 Figure 6.
    
    Reference: Bor+ MSWiM 2016, Figure 6
    At G=1.0, p_s ≈ 0.135 (13.5% success)
    """
    config = LoRaConfig(spreading_factor=9, duty_cycle=0.01)
    
    # 100 nodes, 1% duty cycle → G = 1.0
    network = LPWANNetwork(num_nodes=100, lora_config=config, seed=42)
    
    p_s = network.compute_collision_probability()
    expected_p_s = np.exp(-2 * 1.0)  # ≈ 0.135
    
    assert abs(p_s - expected_p_s) < 0.01, f"p_s={p_s:.3f}, expected {expected_p_s:.3f}"
    print(f"✓ Collision probability: p_s={p_s:.3f} (matches Bor+ 2016)")


def test_duty_cycle_enforcement():
    """Test that duty cycle prevents rapid retransmissions."""
    config = LoRaConfig(spreading_factor=9, duty_cycle=0.01)
    network = LPWANNetwork(num_nodes=10, lora_config=config, seed=42)
    
    # First transmission should succeed
    success1 = network.transmit(node_id=0, payload={"data": 1})
    assert success1, "First transmission should succeed"
    
    # Immediate second transmission should fail (duty cycle blocked)
    success2 = network.transmit(node_id=0, payload={"data": 2})
    assert not success2, "Immediate retransmission should be blocked"
    
    # Check wait time
    can_tx, wait_time = network.can_transmit(node_id=0)
    assert not can_tx, "Should not be able to transmit yet"
    assert wait_time is not None and wait_time > 0, "Should have non-zero wait time"
    
    print(f"✓ Duty cycle enforced: wait {wait_time:.1f}s before next TX")


def test_network_statistics():
    """Test network statistics tracking."""
    config = LoRaConfig(spreading_factor=9, duty_cycle=0.01)
    network = LPWANNetwork(num_nodes=50, lora_config=config, seed=42)
    
    # Send some packets
    for i in range(10):
        network.transmit(node_id=i, payload={"round": 1, "value": 25.0})
    
    stats = network.get_statistics()
    
    assert stats['packets_sent'] == 10
    assert stats['offered_load_G'] == 50 * 0.01  # N * D = 0.5
    assert 0 < stats['theoretical_success_prob'] < 1
    
    print(f"✓ Network stats: G={stats['offered_load_G']}, p_s={stats['theoretical_success_prob']:.3f}")


if __name__ == "__main__":
    print("Running network layer validation tests...\n")
    test_airtime_calculation_sf9()
    test_collision_probability_matches_bor2016()
    test_duty_cycle_enforcement()
    test_network_statistics()
    print("\n✅ All tests passed! Network model validated against published research.")

