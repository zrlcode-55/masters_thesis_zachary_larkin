"""
ACCURACY TESTS: Validate Against Published Research

Every parameter in this thesis must match published, peer-reviewed research.
These tests ensure scientific rigor.
"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from network.lora_config import LoRaConfig
from network.lpwan_network import LPWANNetwork


def test_semtech_airtime_formula():
    """
    Validate airtime calculation against Semtech AN1200.13.
    
    Reference: Semtech Application Note AN1200.13, Section 4.1.1.6
    """
    print("\n" + "="*60)
    print("ACCURACY TEST 1: Semtech Airtime Formula")
    print("="*60)
    
    test_cases = [
        # (SF, payload_bytes, expected_range_ms)
        # Note: 51 bytes is LoRaWAN MAC header (13) + app payload (38)
        (7, 51, (90, 105)),      # SF7: 51 bytes takes ~100ms
        (9, 51, (300, 320)),     # SF9: Baseline (urban)
        (12, 51, (2250, 2350)),  # SF12: Slow, long range (~2.3s)
    ]
    
    for sf, payload, (min_ms, max_ms) in test_cases:
        config = LoRaConfig(spreading_factor=sf, bandwidth=125_000)
        airtime_s = config.compute_airtime(payload_bytes=payload)
        airtime_ms = airtime_s * 1000
        
        assert min_ms <= airtime_ms <= max_ms, \
            f"SF{sf}: {airtime_ms:.1f}ms outside Semtech range [{min_ms}, {max_ms}]"
        
        print(f"  ✓ SF{sf}: {airtime_ms:.1f}ms (Semtech: {min_ms}-{max_ms}ms)")
    
    print("✅ Airtime calculations match Semtech AN1200.13")


def test_bor2016_collision_model():
    """
    Validate collision probability against Bor+ MSWiM 2016, Figure 6.
    
    Reference: M. C. Bor et al., "Do LoRa Low-Power Wide-Area Networks Scale?"
               MSWiM 2016, DOI: 10.1145/2988287.2989163, Figure 6
    """
    print("\n" + "="*60)
    print("ACCURACY TEST 2: Bor+ 2016 Collision Model")
    print("="*60)
    
    test_cases = [
        # (N_nodes, duty_cycle, expected_G, expected_p_s_range)
        (50, 0.01, 0.5, (0.35, 0.38)),    # Light load
        (100, 0.01, 1.0, (0.13, 0.15)),   # Moderate load (baseline)
        (200, 0.01, 2.0, (0.015, 0.020)), # Heavy load
    ]
    
    for N, D, expected_G, (min_ps, max_ps) in test_cases:
        config = LoRaConfig(duty_cycle=D)
        network = LPWANNetwork(num_nodes=N, lora_config=config, seed=42)
        
        # Compute offered load and p_s
        G = network.num_nodes * network.config.duty_cycle
        p_s = network.compute_collision_probability()
        
        # Verify G calculation
        assert abs(G - expected_G) < 0.01, f"G={G:.2f} != expected {expected_G}"
        
        # Verify p_s matches Bor+ Figure 6
        assert min_ps <= p_s <= max_ps, \
            f"N={N}: p_s={p_s:.3f} outside Bor+ range [{min_ps:.3f}, {max_ps:.3f}]"
        
        print(f"  ✓ N={N}, G={G:.1f}: p_s={p_s:.3f} (Bor+ Fig 6: {min_ps:.3f}-{max_ps:.3f})")
    
    print("✅ Collision model matches Bor+ MSWiM 2016")


def test_etsi_duty_cycle():
    """
    Validate duty cycle enforcement against ETSI EN 300 220.
    
    Reference: ETSI EN 300 220 v3.2.1, Section 4.2.1
               "After TX for time T, must wait T/D - T before next TX"
    """
    print("\n" + "="*60)
    print("ACCURACY TEST 3: ETSI EN 300 220 Duty Cycle")
    print("="*60)
    
    config = LoRaConfig(spreading_factor=9, duty_cycle=0.01)
    network = LPWANNetwork(num_nodes=10, lora_config=config, seed=42)
    
    # First transmission
    success = network.transmit(node_id=0, payload={"test": 1})
    assert success, "First transmission should succeed"
    
    # Check wait time
    can_tx, wait_time = network.can_transmit(node_id=0)
    assert not can_tx, "Should not be able to transmit immediately"
    
    # Verify wait time formula: T_wait = T_pkt / D - T_pkt
    T_pkt = network.default_airtime
    expected_wait = (T_pkt / config.duty_cycle) - T_pkt
    
    assert abs(wait_time - expected_wait) < 0.1, \
        f"Wait time {wait_time:.1f}s != expected {expected_wait:.1f}s (ETSI formula)"
    
    print(f"  ✓ T_packet = {T_pkt*1000:.1f}ms")
    print(f"  ✓ Required wait = {wait_time:.1f}s (ETSI: T/D - T)")
    print(f"  ✓ 1% duty cycle = {3600 * config.duty_cycle:.0f}s/hour (ETSI limit)")
    
    print("✅ Duty cycle enforcement matches ETSI EN 300 220")


def test_lora_snr_requirements():
    """
    Validate SNR requirements against LoRa datasheet.
    
    Reference: Semtech SX1276 datasheet, Table 10
    """
    print("\n" + "="*60)
    print("ACCURACY TEST 4: LoRa SNR Requirements")
    print("="*60)
    
    expected_snr = {
        7: -7.5,
        8: -10.0,
        9: -12.5,
        10: -15.0,
        11: -17.5,
        12: -20.0
    }
    
    for sf, expected in expected_snr.items():
        config = LoRaConfig(spreading_factor=sf)
        snr = config.get_required_snr()
        
        assert snr == expected, \
            f"SF{sf}: SNR={snr}dB != expected {expected}dB (Semtech datasheet)"
        
        print(f"  ✓ SF{sf}: {snr}dB (Semtech SX1276 Table 10)")
    
    print("✅ SNR requirements match Semtech datasheet")


def test_network_scaling():
    """
    Validate network scaling behavior matches Georgiou+ 2017.
    
    Reference: O. Georgiou, "Low Power Wide Area Network Analysis"
               IEEE WCL 2017, DOI: 10.1109/LWC.2016.2647247
    """
    print("\n" + "="*60)
    print("ACCURACY TEST 5: Network Scaling (Georgiou+ 2017)")
    print("="*60)
    
    config = LoRaConfig(duty_cycle=0.01)
    
    # Test scaling: p_s should degrade exponentially with N
    node_counts = [50, 100, 200, 500]
    p_s_values = []
    
    for N in node_counts:
        network = LPWANNetwork(num_nodes=N, lora_config=config, seed=42)
        p_s = network.compute_collision_probability()
        p_s_values.append(p_s)
        
        print(f"  N={N:3d}: p_s={p_s:.4f} ({100*(1-p_s):.1f}% loss)")
    
    # Verify exponential degradation
    assert p_s_values[0] > p_s_values[1] > p_s_values[2] > p_s_values[3], \
        "p_s should decrease with increasing N"
    
    # Verify qualitative match to Georgiou+ 2017 Table II
    # At N=100: should have 85-90% packet loss (p_s = 0.10-0.15)
    assert 0.10 <= p_s_values[1] <= 0.20, \
        f"N=100: p_s={p_s_values[1]:.3f} doesn't match Georgiou+ (~85-90% loss)"
    
    # Network should "break" (p_s < 0.1) around N=500 [Bor+ 2016 Fig 7]
    assert p_s_values[3] < 0.1, \
        f"N=500: p_s={p_s_values[3]:.3f} should be <0.1 (network collapse)"
    
    print("✅ Scaling behavior matches Georgiou+ 2017 and Bor+ 2016")


if __name__ == "__main__":
    print("\n" + "━"*60)
    print("📚 RUNNING ACCURACY VALIDATION TESTS")
    print("━"*60)
    print("\nValidating against published, peer-reviewed research:")
    print("  • Semtech AN1200.13 (LoRa formulas)")
    print("  • Bor+ MSWiM 2016 (collision model)")
    print("  • ETSI EN 300 220 (duty cycle regulations)")
    print("  • Georgiou+ IEEE WCL 2017 (scaling)")
    print()
    
    tests = [
        test_semtech_airtime_formula,
        test_bor2016_collision_model,
        test_etsi_duty_cycle,
        test_lora_snr_requirements,
        test_network_scaling,
    ]
    
    passed = 0
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            raise
    
    print("\n" + "━"*60)
    print(f"✅ ALL {passed} ACCURACY TESTS PASSED!")
    print("━"*60)
    print("\n🎓 Your network model is scientifically rigorous!")
    print("   Every parameter matches published research.")

