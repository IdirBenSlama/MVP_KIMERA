# KIMERA Real-World Test Suite

## 🌍 Overview

The KIMERA Real-World Test Suite is a comprehensive testing framework that validates KIMERA's cognitive capabilities across multiple realistic domains. This test suite goes beyond simple unit tests to demonstrate how KIMERA handles complex, contradictory information in scenarios that mirror real-world complexity.

## 🎯 What It Tests

### Core Capabilities Validated
- **Contradiction Detection**: Ability to identify semantic contradictions in complex scenarios
- **Cross-Domain Learning**: Learning patterns that apply across different domains
- **Adaptive Processing**: Maintaining system stability while processing conflicting information
- **Cognitive Coherence**: Preserving logical consistency under stress
- **Real-Time Processing**: Performance under realistic data loads

### Domains Tested

#### 1. 💰 Financial Markets
- **Bull vs Bear Market Dynamics**: Contradictory market sentiment patterns
- **Market Euphoria vs Risk Signals**: High sentiment with dangerous volatility
- **Flight to Safety**: Counter-intuitive low volatility during crisis
- **Tests**: Market psychology contradictions, volatility patterns

#### 2. 🌦️ Weather Systems  
- **High Pressure Clear Weather**: Stable atmospheric conditions
- **Low Pressure Storm Systems**: Dynamic weather patterns
- **Temperature Inversions**: Unusual atmospheric phenomena
- **Microclimate Anomalies**: Localized weather contradictions
- **Tests**: Causal relationships, temporal predictions

#### 3. 👥 Social Dynamics
- **Group Consensus**: High-functioning team dynamics
- **Group Polarization**: Conflict and low trust scenarios
- **False Consensus**: Surface harmony hiding tensions
- **Emergent Leadership**: Leadership arising from moderate conditions
- **Tests**: Psychological contradictions, group behavior patterns

#### 4. 🔬 Scientific Discovery
- **Established Theories**: Well-supported scientific frameworks
- **Anomalous Observations**: Data that challenges existing theories
- **Competing Hypotheses**: Alternative explanatory frameworks
- **Paradigm Shift Evidence**: Revolutionary scientific insights
- **Tests**: Evidence evaluation, hypothesis conflicts

#### 5. 🚨 Crisis Management
- **Resource Abundance**: Low-stress decision making
- **Resource Scarcity**: High-pressure emergency response
- **Information Paradox**: Clear data with stakeholder disagreement
- **False Calm**: Hidden dangers masquerading as stability
- **Tests**: Decision making under uncertainty, rapid adaptation

## 🚀 Quick Start

### Option 1: Automated Launch (Recommended)

**Windows:**
```bash
start_real_world_test.bat
```

**Unix/Linux/Mac:**
```bash
./start_real_world_test.sh
```

These scripts will:
1. Check if KIMERA is running
2. Start KIMERA if needed
3. Wait for system readiness
4. Run the comprehensive test suite
5. Generate detailed reports

### Option 2: Manual Launch

1. **Start KIMERA System:**
   ```bash
   python run_kimera.py
   ```
   Wait for "Server will start on http://localhost:XXXX" message.

2. **Run Test Suite:**
   ```bash
   python run_real_world_test.py
   ```

## 📊 Understanding the Results

### Test Output Files

#### 1. **Execution Log** (`real_world_test_YYYYMMDD_HHMMSS.log`)
- Real-time test execution details
- System health checks
- Contradiction detection results
- Error messages and warnings

#### 2. **Detailed Results** (`real_world_test_results_YYYYMMDD_HHMMSS.json`)
- Complete test data in JSON format
- Geoid IDs created during testing
- System metrics before/after
- Cross-domain analysis results

### Key Metrics to Watch

#### Contradiction Detection
- **Total Contradictions Found**: Higher numbers indicate active contradiction detection
- **Domain Distribution**: Which domains generated the most contradictions
- **Processing Success Rate**: Percentage of successful contradiction processing

#### System Performance
- **Geoid Creation Success**: All scenarios should create geoids successfully
- **API Response Times**: Should remain stable throughout testing
- **System Stability**: Entropy and complexity metrics should remain within bounds

#### Cross-Domain Insights
- **Pattern Recognition**: System's ability to identify patterns across domains
- **Adaptation Evidence**: How the system adjusts to different types of contradictions
- **Learning Transfer**: Evidence of knowledge transfer between domains

## 🔍 Interpreting Results

### ✅ Good Results Indicators
- **High Contradiction Detection**: 10+ contradictions across all domains
- **100% Geoid Creation Success**: All scenarios create geoids successfully
- **Stable System Metrics**: Entropy remains controlled, no system crashes
- **Cross-Domain Patterns**: System identifies patterns across multiple domains
- **High Processing Success Rate**: >90% success rate for API calls

### ⚠️ Warning Signs
- **No Contradictions Detected**: May indicate system not functioning properly
- **Failed Geoid Creation**: Network or system configuration issues
- **High Error Rates**: System instability or resource constraints
- **Inconsistent Performance**: Possible memory leaks or resource exhaustion

### ❌ Failure Indicators
- **System Unavailable**: KIMERA not running or not accessible
- **Multiple API Failures**: Serious system or network issues
- **Crash During Testing**: System instability under load
- **No Cross-Domain Patterns**: Cognitive processing not functioning

## 🛠️ Troubleshooting

### Common Issues

#### "KIMERA API not accessible"
- **Solution**: Start KIMERA with `python run_kimera.py`
- **Check**: Firewall settings, port availability (8001-8010)
- **Verify**: Visit `http://localhost:8001/docs` in browser

#### "No contradictions detected"
- **Possible Causes**: 
  - System not processing contradictions properly
  - Threshold settings too restrictive
  - Embedding model issues
- **Solution**: Check system logs, verify contradiction engine status

#### "High error rates"
- **Possible Causes**:
  - System resource constraints
  - Network timeouts
  - Database connectivity issues
- **Solution**: Check system resources, restart KIMERA, verify database connection

#### "Test suite hangs or crashes"
- **Possible Causes**:
  - Memory exhaustion
  - Infinite loops in processing
  - Database locks
- **Solution**: Restart KIMERA, check system resources, review logs

### Performance Optimization

#### For Better Results
1. **Ensure Adequate Resources**: 8GB+ RAM recommended
2. **Close Other Applications**: Reduce system load during testing
3. **Use SSD Storage**: Faster I/O improves performance
4. **Stable Network**: Reliable connection for API calls

#### For Faster Execution
1. **Reduce Scenario Complexity**: Modify test scenarios if needed
2. **Adjust Timeouts**: Increase timeout values for slower systems
3. **Sequential Processing**: Disable parallel processing if needed

## 📈 Advanced Usage

### Customizing Test Scenarios

Edit `run_real_world_test.py` to modify:
- **Semantic Features**: Adjust contradiction intensity
- **Scenario Complexity**: Add/remove test cases
- **Processing Parameters**: Modify search limits, timeouts
- **Reporting Detail**: Change logging levels, output formats

### Integration with CI/CD

The test suite can be integrated into automated testing pipelines:

```bash
# Example CI/CD integration
python run_real_world_test.py --automated --no-interactive
```

### Batch Testing

Run multiple test sessions:
```bash
for i in {1..5}; do
    echo "Running test session $i"
    python run_real_world_test.py
    sleep 60  # Wait between sessions
done
```

## 📋 Test Scenarios Details

### Financial Market Contradictions
- **Bull vs Bear**: Same sector with opposite momentum
- **Euphoria + Volatility**: High sentiment with high risk
- **Crisis + Stability**: Flight to safety during turmoil

### Weather Pattern Contradictions  
- **Temperature Inversions**: Hot air under cold air
- **Microclimate Anomalies**: Local weather defying regional patterns
- **Pressure-Wind Conflicts**: Unexpected wind patterns

### Social Dynamic Contradictions
- **False Consensus**: High cooperation, low trust
- **Hidden Conflict**: Apparent harmony, underlying tension
- **Leadership Paradox**: Strong leadership from weak foundations

### Scientific Method Contradictions
- **Evidence vs Acceptance**: Strong evidence, low peer acceptance
- **Theory vs Observation**: Established theory, contradictory data
- **Paradigm Resistance**: Revolutionary evidence, institutional resistance

### Crisis Management Contradictions
- **False Calm**: Low urgency, high actual risk
- **Information Paradox**: Clear data, stakeholder disagreement
- **Resource Illusion**: Apparent abundance, hidden scarcity

## 🎯 Success Criteria

### Minimum Viable Results
- [ ] System starts and responds to health checks
- [ ] At least 50% of geoids created successfully
- [ ] At least 1 contradiction detected per domain
- [ ] Test completes without system crashes
- [ ] Generates readable report

### Optimal Results
- [ ] 100% geoid creation success rate
- [ ] 5+ contradictions detected per domain
- [ ] <5% API call failure rate
- [ ] Cross-domain patterns identified
- [ ] System maintains stability throughout

### Exceptional Results
- [ ] 10+ contradictions per domain
- [ ] Complex multi-domain patterns detected
- [ ] System shows adaptive behavior
- [ ] Evidence of learning and memory formation
- [ ] Insights applicable to real-world scenarios

## 🔬 Research Applications

This test suite can be used for:
- **Cognitive Architecture Research**: Understanding AI reasoning patterns
- **Contradiction Processing Studies**: How AI handles conflicting information
- **Cross-Domain Learning**: Transfer of insights between domains
- **System Stability Analysis**: AI behavior under cognitive stress
- **Real-World AI Validation**: Practical AI capability assessment

## 📚 Further Reading

- **KIMERA Documentation**: `docs/` directory
- **System Architecture**: `docs/01_architecture/`
- **API Reference**: `http://localhost:8001/docs` (when running)
- **Development Guide**: `DEVELOPMENT_ROADMAP.md`
- **Quick Start**: `QUICK_START_GUIDE.md`

---

## 🤝 Contributing

To improve the test suite:
1. Add new domain scenarios
2. Enhance contradiction patterns
3. Improve result analysis
4. Add visualization capabilities
5. Optimize performance

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review generated log files
3. Verify system requirements
4. Check KIMERA system status
5. Consult the main project documentation

---

**Ready to test KIMERA's real-world capabilities? Run the test suite and discover how AI handles the complexity of realistic scenarios!** 🚀 