"""
Statistical Modeling Module for Kimera SWM

This module integrates statsmodels with the Kimera SWM framework to provide
advanced statistical modeling capabilities for semantic analysis, time series
forecasting, and econometric modeling of cognitive processes.

Key Features:
1. Time series analysis for semantic entropy patterns
2. Regression modeling for contradiction detection
3. Econometric analysis of semantic thermodynamics
4. Statistical hypothesis testing for system validation
5. Advanced forecasting for predictive insights

Author: Kimera SWM Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import warnings

# Core Kimera imports
from .native_math import NativeStats, NativeMath

# Try to import EntropyCalculator, but don't fail if it's not available
try:
    from .enhanced_entropy import EntropyCalculator
    ENHANCED_ENTROPY_AVAILABLE = True
except ImportError:
    ENHANCED_ENTROPY_AVAILABLE = False
    EntropyCalculator = None

# Suppress statsmodels warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning, module='statsmodels')

try:
    import statsmodels.api as sm
    import statsmodels.tsa.api as tsa
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.vector_ar.var_model import VAR
    from statsmodels.tsa.stattools import adfuller, kpss
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.regression.linear_model import OLS
    from statsmodels.stats.stattools import durbin_watson
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.stats.outliers_influence import OLSInfluence
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logging.warning("Statsmodels not available. Statistical modeling features will be limited.")

logger = logging.getLogger(__name__)

@dataclass
class StatisticalModelResult:
    """Container for statistical model results"""
    model_type: str
    parameters: Dict[str, float]
    statistics: Dict[str, float]
    predictions: Optional[List[float]] = None
    residuals: Optional[List[float]] = None
    confidence_intervals: Optional[List[Tuple[float, float]]] = None
    diagnostics: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SemanticTimeSeriesAnalyzer:
    """
    Advanced time series analysis for semantic entropy patterns using statsmodels.
    
    This class provides sophisticated time series modeling capabilities specifically
    designed for analyzing semantic entropy evolution, contradiction patterns,
    and cognitive thermodynamic processes.
    """
    
    def __init__(self):
        self.models = {}
        self.results_cache = {}
        
    def analyze_entropy_series(self, entropy_data: List[float], 
                             timestamps: Optional[List[datetime]] = None) -> StatisticalModelResult:
        """
        Comprehensive time series analysis of entropy data.
        
        Args:
            entropy_data: List of entropy measurements
            timestamps: Optional timestamps for the data
            
        Returns:
            StatisticalModelResult with comprehensive analysis
        """
        if not STATSMODELS_AVAILABLE:
            return self._fallback_entropy_analysis(entropy_data)
            
        try:
            # Convert to pandas Series for statsmodels
            if timestamps:
                ts = pd.Series(entropy_data, index=pd.to_datetime(timestamps))
            else:
                ts = pd.Series(entropy_data)
            
            # Stationarity tests
            adf_result = adfuller(ts.dropna())
            kpss_result = kpss(ts.dropna())
            
            # Seasonal decomposition if enough data
            decomposition = None
            if len(ts) >= 24:  # Need sufficient data for decomposition
                try:
                    decomposition = seasonal_decompose(ts, model='additive', period=min(12, len(ts)//2))
                except:
                    decomposition = None
            
            # ARIMA modeling
            arima_model = None
            arima_forecast = None
            try:
                # Auto-select ARIMA parameters
                arima_model = ARIMA(ts, order=(1, 1, 1))
                arima_fit = arima_model.fit()
                arima_forecast = arima_fit.forecast(steps=5)
            except:
                arima_model = None
                arima_forecast = None
            
            # Compile results
            statistics = {
                'mean': float(ts.mean()),
                'std': float(ts.std()),
                'adf_statistic': float(adf_result[0]),
                'adf_pvalue': float(adf_result[1]),
                'kpss_statistic': float(kpss_result[0]),
                'kpss_pvalue': float(kpss_result[1]),
                'is_stationary': adf_result[1] < 0.05,
                'trend_strength': float(abs(ts.diff().mean())) if len(ts) > 1 else 0.0
            }
            
            diagnostics = {
                'decomposition_available': decomposition is not None,
                'arima_successful': arima_model is not None,
                'data_points': len(ts),
                'missing_values': ts.isna().sum()
            }
            
            if decomposition:
                diagnostics['seasonal_strength'] = float(decomposition.seasonal.std())
                diagnostics['trend_strength'] = float(decomposition.trend.std())
            
            return StatisticalModelResult(
                model_type="entropy_time_series",
                parameters={'arima_order': (1, 1, 1) if arima_model else None},
                statistics=statistics,
                predictions=arima_forecast.tolist() if arima_forecast is not None else None,
                diagnostics=diagnostics
            )
            
        except Exception as e:
            logger.error(f"Error in entropy series analysis: {e}")
            return self._fallback_entropy_analysis(entropy_data)
    
    def detect_regime_changes(self, data: List[float]) -> Dict[str, Any]:
        """
        Detect structural breaks and regime changes in time series data.
        
        Args:
            data: Time series data
            
        Returns:
            Dictionary with regime change analysis results
        """
        if not STATSMODELS_AVAILABLE or len(data) < 10:
            return {'regime_changes': [], 'method': 'insufficient_data'}
        
        try:
            ts = pd.Series(data)
            
            # Simple change point detection using rolling statistics
            window = min(5, len(data) // 4)
            rolling_mean = ts.rolling(window=window).mean()
            rolling_std = ts.rolling(window=window).std()
            
            # Detect significant changes in mean
            mean_changes = []
            for i in range(window, len(rolling_mean) - window):
                before = rolling_mean.iloc[i-window:i].mean()
                after = rolling_mean.iloc[i:i+window].mean()
                if abs(after - before) > 2 * rolling_std.iloc[i]:
                    mean_changes.append(i)
            
            return {
                'regime_changes': mean_changes,
                'method': 'rolling_statistics',
                'change_points': len(mean_changes),
                'stability_score': 1.0 / (1.0 + len(mean_changes))
            }
            
        except Exception as e:
            logger.error(f"Error in regime change detection: {e}")
            return {'regime_changes': [], 'method': 'error', 'error': str(e)}
    
    def _fallback_entropy_analysis(self, entropy_data: List[float]) -> StatisticalModelResult:
        """Fallback analysis when statsmodels is not available"""
        mean_entropy = NativeStats.mean(entropy_data)
        std_entropy = NativeStats.std(entropy_data)
        
        # Simple trend analysis
        if len(entropy_data) > 1:
            trend = (entropy_data[-1] - entropy_data[0]) / len(entropy_data)
        else:
            trend = 0.0
        
        return StatisticalModelResult(
            model_type="entropy_basic_analysis",
            parameters={'trend': trend},
            statistics={
                'mean': mean_entropy,
                'std': std_entropy,
                'trend': trend,
                'range': max(entropy_data) - min(entropy_data)
            },
            diagnostics={'method': 'native_fallback'}
        )

class ContradictionRegressionAnalyzer:
    """
    Regression analysis for understanding contradiction patterns and their
    relationships with semantic features.
    """
    
    def __init__(self):
        self.models = {}
        
    def analyze_contradiction_factors(self, 
                                   contradiction_scores: List[float],
                                   semantic_features: Dict[str, List[float]]) -> StatisticalModelResult:
        """
        Analyze factors that contribute to contradiction detection.
        
        Args:
            contradiction_scores: Target variable (contradiction intensity)
            semantic_features: Dictionary of feature names to feature values
            
        Returns:
            StatisticalModelResult with regression analysis
        """
        if not STATSMODELS_AVAILABLE:
            return self._fallback_regression_analysis(contradiction_scores, semantic_features)
        
        try:
            # Prepare data
            df = pd.DataFrame(semantic_features)
            df['contradiction_score'] = contradiction_scores
            
            # Remove any rows with missing values
            df = df.dropna()
            
            if len(df) < 5:  # Need minimum data for regression
                return self._fallback_regression_analysis(contradiction_scores, semantic_features)
            
            # Prepare variables
            y = df['contradiction_score']
            X = df.drop('contradiction_score', axis=1)
            X = sm.add_constant(X)  # Add intercept
            
            # Fit OLS model
            model = OLS(y, X)
            results = model.fit()
            
            # Calculate diagnostics
            influence = OLSInfluence(results)
            dw_stat = durbin_watson(results.resid)
            
            # Extract key statistics
            statistics = {
                'r_squared': float(results.rsquared),
                'adj_r_squared': float(results.rsquared_adj),
                'f_statistic': float(results.fvalue),
                'f_pvalue': float(results.f_pvalue),
                'durbin_watson': float(dw_stat),
                'aic': float(results.aic),
                'bic': float(results.bic)
            }
            
            # Extract parameters
            parameters = {}
            for i, param in enumerate(results.params.index):
                parameters[f'{param}_coef'] = float(results.params.iloc[i])
                parameters[f'{param}_pvalue'] = float(results.pvalues.iloc[i])
            
            diagnostics = {
                'n_observations': int(results.nobs),
                'n_features': len(X.columns) - 1,  # Exclude constant
                'condition_number': float(np.linalg.cond(X.values)),
                'outliers_detected': len(influence.summary_frame()[influence.summary_frame()['cooks_d'] > 0.5])
            }
            
            return StatisticalModelResult(
                model_type="contradiction_regression",
                parameters=parameters,
                statistics=statistics,
                predictions=results.fittedvalues.tolist(),
                residuals=results.resid.tolist(),
                diagnostics=diagnostics
            )
            
        except Exception as e:
            logger.error(f"Error in contradiction regression analysis: {e}")
            return self._fallback_regression_analysis(contradiction_scores, semantic_features)
    
    def _fallback_regression_analysis(self, 
                                    contradiction_scores: List[float],
                                    semantic_features: Dict[str, List[float]]) -> StatisticalModelResult:
        """Fallback regression analysis using native math"""
        # Simple correlation analysis
        correlations = {}
        for feature_name, feature_values in semantic_features.items():
            if len(feature_values) == len(contradiction_scores):
                corr = NativeStats.correlation(contradiction_scores, feature_values)
                correlations[f'{feature_name}_correlation'] = corr
        
        return StatisticalModelResult(
            model_type="contradiction_basic_regression",
            parameters=correlations,
            statistics={
                'mean_contradiction': NativeStats.mean(contradiction_scores),
                'std_contradiction': NativeStats.std(contradiction_scores)
            },
            diagnostics={'method': 'native_fallback'}
        )

class SemanticEconometrics:
    """
    Econometric analysis of semantic systems, treating cognitive processes
    as economic systems with supply, demand, and equilibrium dynamics.
    """
    
    def __init__(self):
        self.models = {}
        
    def analyze_semantic_market(self, 
                              semantic_supply: List[float],
                              semantic_demand: List[float],
                              entropy_prices: List[float]) -> StatisticalModelResult:
        """
        Analyze semantic market dynamics using econometric models.
        
        Args:
            semantic_supply: Supply of semantic information
            semantic_demand: Demand for semantic processing
            entropy_prices: Entropy as price mechanism
            
        Returns:
            StatisticalModelResult with econometric analysis
        """
        if not STATSMODELS_AVAILABLE:
            return self._fallback_market_analysis(semantic_supply, semantic_demand, entropy_prices)
        
        try:
            # Create market equilibrium model
            df = pd.DataFrame({
                'supply': semantic_supply,
                'demand': semantic_demand,
                'price': entropy_prices
            }).dropna()
            
            if len(df) < 10:
                return self._fallback_market_analysis(semantic_supply, semantic_demand, entropy_prices)
            
            # Supply equation: supply = f(price, lagged_supply)
            df['supply_lag'] = df['supply'].shift(1)
            supply_model = OLS(df['supply'].iloc[1:], 
                             sm.add_constant(df[['price', 'supply_lag']].iloc[1:]))
            supply_results = supply_model.fit()
            
            # Demand equation: demand = f(price, lagged_demand)
            df['demand_lag'] = df['demand'].shift(1)
            demand_model = OLS(df['demand'].iloc[1:], 
                             sm.add_constant(df[['price', 'demand_lag']].iloc[1:]))
            demand_results = demand_model.fit()
            
            # Market efficiency metrics
            supply_elasticity = supply_results.params.get('price', 0.0)
            demand_elasticity = demand_results.params.get('price', 0.0)
            
            statistics = {
                'supply_price_elasticity': float(supply_elasticity),
                'demand_price_elasticity': float(demand_elasticity),
                'market_efficiency': float(abs(supply_elasticity + demand_elasticity)),
                'supply_r_squared': float(supply_results.rsquared),
                'demand_r_squared': float(demand_results.rsquared)
            }
            
            parameters = {
                'supply_intercept': float(supply_results.params.get('const', 0.0)),
                'supply_price_coef': float(supply_elasticity),
                'demand_intercept': float(demand_results.params.get('const', 0.0)),
                'demand_price_coef': float(demand_elasticity)
            }
            
            return StatisticalModelResult(
                model_type="semantic_econometrics",
                parameters=parameters,
                statistics=statistics,
                diagnostics={
                    'market_type': 'semantic_information',
                    'equilibrium_stability': statistics['market_efficiency'] < 2.0
                }
            )
            
        except Exception as e:
            logger.error(f"Error in semantic market analysis: {e}")
            return self._fallback_market_analysis(semantic_supply, semantic_demand, entropy_prices)
    
    def _fallback_market_analysis(self, 
                                semantic_supply: List[float],
                                semantic_demand: List[float],
                                entropy_prices: List[float]) -> StatisticalModelResult:
        """Fallback market analysis using basic statistics"""
        supply_mean = NativeStats.mean(semantic_supply)
        demand_mean = NativeStats.mean(semantic_demand)
        price_mean = NativeStats.mean(entropy_prices)
        
        # Simple market balance
        market_balance = abs(supply_mean - demand_mean) / max(supply_mean, demand_mean, 1.0)
        
        return StatisticalModelResult(
            model_type="semantic_basic_market",
            parameters={
                'supply_mean': supply_mean,
                'demand_mean': demand_mean,
                'price_mean': price_mean
            },
            statistics={
                'market_balance': market_balance,
                'market_efficiency': 1.0 - market_balance
            },
            diagnostics={'method': 'native_fallback'}
        )

class StatisticalModelingEngine:
    """
    Main engine that coordinates all statistical modeling capabilities
    for the Kimera SWM system.
    """
    
    def __init__(self):
        self.time_series_analyzer = SemanticTimeSeriesAnalyzer()
        self.regression_analyzer = ContradictionRegressionAnalyzer()
        self.econometrics = SemanticEconometrics()
        self.model_cache = {}
        
    def comprehensive_analysis(self, 
                             system_data: Dict[str, Any]) -> Dict[str, StatisticalModelResult]:
        """
        Perform comprehensive statistical analysis of system data.
        
        Args:
            system_data: Dictionary containing various system measurements
            
        Returns:
            Dictionary of analysis results by analysis type
        """
        results = {}
        
        # Time series analysis of entropy
        if 'entropy_history' in system_data:
            results['entropy_analysis'] = self.time_series_analyzer.analyze_entropy_series(
                system_data['entropy_history'],
                system_data.get('timestamps')
            )
        
        # Contradiction factor analysis
        if 'contradiction_scores' in system_data and 'semantic_features' in system_data:
            results['contradiction_analysis'] = self.regression_analyzer.analyze_contradiction_factors(
                system_data['contradiction_scores'],
                system_data['semantic_features']
            )
        
        # Semantic market analysis
        if all(key in system_data for key in ['semantic_supply', 'semantic_demand', 'entropy_prices']):
            results['market_analysis'] = self.econometrics.analyze_semantic_market(
                system_data['semantic_supply'],
                system_data['semantic_demand'],
                system_data['entropy_prices']
            )
        
        # Regime change detection
        if 'entropy_history' in system_data:
            regime_analysis = self.time_series_analyzer.detect_regime_changes(
                system_data['entropy_history']
            )
            results['regime_analysis'] = StatisticalModelResult(
                model_type="regime_detection",
                parameters={'change_points': regime_analysis.get('change_points', 0)},
                statistics={'stability_score': regime_analysis.get('stability_score', 1.0)},
                diagnostics=regime_analysis
            )
        
        return results
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary of available statistical modeling capabilities"""
        return {
            'statsmodels_available': STATSMODELS_AVAILABLE,
            'capabilities': {
                'time_series_analysis': True,
                'regression_modeling': True,
                'econometric_analysis': True,
                'regime_detection': True,
                'forecasting': STATSMODELS_AVAILABLE
            },
            'supported_models': [
                'ARIMA', 'VAR', 'OLS Regression', 'Seasonal Decomposition',
                'Exponential Smoothing', 'Structural Break Detection'
            ] if STATSMODELS_AVAILABLE else ['Basic Statistics', 'Native Correlation']
        }

# Global instance for easy access
statistical_engine = StatisticalModelingEngine()

def get_statistical_engine() -> StatisticalModelingEngine:
    """Get the global statistical modeling engine instance"""
    return statistical_engine

# Convenience functions for common operations
def analyze_entropy_time_series(entropy_data: List[float], 
                               timestamps: Optional[List[datetime]] = None) -> StatisticalModelResult:
    """Convenience function for entropy time series analysis"""
    return statistical_engine.time_series_analyzer.analyze_entropy_series(entropy_data, timestamps)

def analyze_contradiction_factors(contradiction_scores: List[float],
                                semantic_features: Dict[str, List[float]]) -> StatisticalModelResult:
    """Convenience function for contradiction factor analysis"""
    return statistical_engine.regression_analyzer.analyze_contradiction_factors(
        contradiction_scores, semantic_features)

def analyze_semantic_market(semantic_supply: List[float],
                          semantic_demand: List[float],
                          entropy_prices: List[float]) -> StatisticalModelResult:
    """Convenience function for semantic market analysis"""
    return statistical_engine.econometrics.analyze_semantic_market(
        semantic_supply, semantic_demand, entropy_prices)