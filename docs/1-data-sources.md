# Data sources: Wytham Woods 2025

This document outlines the technical specifications for the acoustic monitoring dataset collected in Wytham Woods during the 2025 field season.

<br>

## 1. Sampling design

**Study Area:** Wytham Woods, Oxfordshire
**Year:** 2025

The sampling strategy was designed to capture acoustic diversity across a heterogeneous forest environment, balancing spatial coverage with the detection limits of the hardware.


### Grid configuration
*   **Units:** 81 AudioMoth autonomous recorders.
*   **Layout:** 100 × 100 m regular grid.
*   **Topography:** The grid spans an elevation gradient of ~70–160 m.

### Detection range
Detection probability is non-uniform and depends on species loudness, vegetation density, and weather conditions.
*   **Rationale:** The 100 m spacing was selected to maximize spatial coverage while maintaining partial overlap. This means there will be varying levels of autocorrelation/pseudoreplication for different species.

---

## 2. Equipment & configuration

| Component | Specification |
| :--- | :--- |
| **Recorder** | AudioMoth (Open Acoustic Devices) |
| **Housing** | Custom weatherproof enclosures |
| **Mounting** | Thin stakes at **1.6–1.8 m** above ground level |
| **Firmware** | Custom Bat/Bird Firmware ([Source Code](https://github.com/nilomr/AudioMoth-Wytham-Woods/tree/dev/bats)) |

---

## 3. Recording regimes

The deployment was split into two phases to optimise for bird and bat monitoring.

### Phase 1: Standard bird monitoring

*   **Dates:** 15 February 2025 – 20 July 2025
*   **Sample Rate:** 48 kHz
*   **Gain:** Medium
*   **Cycle:** 60s recording / 300s sleep
*   **Schedule:**
    *   **Pre-sunrise:** 80–120 mins *before* sunrise.
    *   **Post-sunset:** 120–30 mins *after* sunset.
    *   *Note: Schedules used 1-minute rounding.*

### Phase 2: Dual bird & bat monitoring
*Focus: Continued bird monitoring with added high-frequency ultrasonic triggers for bat detection.*

*   **Dates:** 20 July 2025 – 30 Aug 2025 (actual end dates in September will vary by recorder, choose a cutoff)
*   **Sample Rates:** 48 kHz (Audible) & 250 kHz (Ultrasonic)
*   **Key Changes:**
    *   **Added:** 3-hour continuous high-frequency sampling block immediately post-sunset for bats.
    *   **Removed:** 1-hour pre-sunset recording block used in Phase 1.
    *   **Firmware:** Switched to custom firmware supporting combined recording modes.

> **Technical note on sample rate transition:**
> Sample rate transition (48 kHz → 250 kHz) was programmed to occur Sun Jul 20 2025 11:00:00 GMT+0

![Sampling Design Map](media/sampling-design.png)


### Clock drift

All AudioMoth devices were synchronised to UTC prior to deployment.

**Deployment window:** 2025-02-15 to 2025-03-18 (~31 days); 23 AudioMoth units assessed.

**Absolute clock drift:** Ranged from 1–100 s, with mean ≈ 42 s and median ≈ 58 s over the deployment (~1.4 s/day on average).

| Direction | Units | Range | Mean | Median |
|-----------|-------|-------|------|--------|
| Ran fast | 7 | 4–63 s | ≈ 27 s | ≈ 22 s |
| Ran slow | 16 | 1–100 s | ≈ 49 s | ≈ 59 s |

<small>For the full clock drift data, see [20250318-clockdrift.csv](../metadata/20250318-clockdrift.csv).</small>

No obvious spatial pattern in drift across grid positions (rows F–J, columns 4–12); variation appears to be primarily between devices. Drift is best interpreted as device-specific oscillator tolerance plus local temperature and power-supply effects.

Approximate average error is consistent with common quartz or MEMS oscillators and with AudioMoth documentation indicating up to about 2 s/day of clock drift. Values are within expectations for low-cost, unsynchronized recorders operating over several weeks, and comparable to typical crystal oscillator tolerances quoted in the electronics literature.

#### Implications for analyses

For most community-level, seasonal, or diel pattern analyses, absolute drifts of up to 1–3 s/day over a month are extremely unlikely to affect inference, especially when aggregating over minutes to 30 or 60 minute bins, as I would encourage. Anything finer-scale than that should probably not be attempted.