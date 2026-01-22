"""
SMC/ICT Strategy Engine for XAUUSD Trading Bot

Implements Smart Money Concepts and Inner Circle Trader methodologies:
- Market structure identification (HH, HL, LH, LL)
- Break of Structure (BOS) detection
- Change of Character (CHoCH) identification
- Order block detection
- Fair Value Gap (FVG) identification
- Liquidity analysis and sweeps
- Premium/Discount zone calculation
- Multi-timeframe alignment

This is the core trading logic of the system.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple, List
from enum import Enum

from config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketStructure(Enum):
    """Enum for market structure types."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    RANGING = "RANGING"
    UNKNOWN = "UNKNOWN"


class TradeSignal(Enum):
    """Enum for trade signals."""
    BUY = "BUY"
    SELL = "SELL"
    NONE = "NONE"


class SMCEngine:
    """
    Smart Money Concepts / Inner Circle Trader Strategy Engine.
    Analyzes market structure and generates trade signals.
    """
    
    def __init__(self):
        """Initialize the SMC Strategy Engine."""
        self.market_bias = {}
        self.current_structure = {}
        self.order_blocks = {}
        self.fair_value_gaps = {}
        self.liquidity_levels = {}
    
    def analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """
        Perform complete SMC/ICT analysis on a single timeframe.
        
        Args:
            df: OHLC DataFrame
            timeframe: Timeframe identifier (D1, H4, H1, M15)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info(f"Analyzing {timeframe} timeframe...")
            
            # Identify swing points
            df = self._identify_swing_points(df)
            
            # Determine market structure
            structure = self._determine_market_structure(df)
            
            # Detect Break of Structure
            bos_detected, bos_type = self._detect_bos(df)
            
            # Detect Change of Character
            choch_detected, choch_type = self._detect_choch(df)
            
            # Identify order blocks
            order_blocks = self._identify_order_blocks(df)
            
            # Identify fair value gaps
            fvgs = self._identify_fair_value_gaps(df)
            
            # Calculate premium/discount zones
            premium_zone, discount_zone = self._calculate_premium_discount(df)
            
            # Identify liquidity levels
            liquidity = self._identify_liquidity_levels(df)
            
            analysis = {
                'timeframe': timeframe,
                'structure': structure,
                'bos_detected': bos_detected,
                'bos_type': bos_type,
                'choch_detected': choch_detected,
                'choch_type': choch_type,
                'order_blocks': order_blocks,
                'fair_value_gaps': fvgs,
                'premium_zone': premium_zone,
                'discount_zone': discount_zone,
                'liquidity_levels': liquidity,
                'current_price': df['close'].iloc[-1]
            }
            
            # Store for multi-timeframe reference
            self.market_bias[timeframe] = analysis
            
            logger.info(f"{timeframe} Analysis Complete: Structure={structure}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {timeframe}: {e}")
            return {}
    
    def _identify_swing_points(self, df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
        """
        Identify swing highs and swing lows.
        
        Args:
            df: OHLC DataFrame
            lookback: Number of candles to check on each side
            
        Returns:
            DataFrame with swing points marked
        """
        df = df.copy()
        df['swing_high'] = False
        df['swing_low'] = False
        df['swing_high_value'] = np.nan
        df['swing_low_value'] = np.nan
        
        for i in range(lookback, len(df) - lookback):
            # Swing High: Current high > all highs in lookback period
            if all(df['high'].iloc[i] > df['high'].iloc[j] 
                   for j in range(i - lookback, i + lookback + 1) if j != i):
                df.loc[df.index[i], 'swing_high'] = True
                df.loc[df.index[i], 'swing_high_value'] = df['high'].iloc[i]
            
            # Swing Low: Current low < all lows in lookback period
            if all(df['low'].iloc[i] < df['low'].iloc[j] 
                   for j in range(i - lookback, i + lookback + 1) if j != i):
                df.loc[df.index[i], 'swing_low'] = True
                df.loc[df.index[i], 'swing_low_value'] = df['low'].iloc[i]
        
        return df
    
    def _determine_market_structure(self, df: pd.DataFrame) -> MarketStructure:
        """
        Determine current market structure based on swing points.
        
        Higher Highs + Higher Lows = Bullish
        Lower Highs + Lower Lows = Bearish
        Mixed = Ranging
        
        Args:
            df: DataFrame with swing points
            
        Returns:
            MarketStructure enum
        """
        try:
            # Get recent swing highs and lows
            swing_highs = df[df['swing_high']]['swing_high_value'].dropna().tail(settings.MIN_SWING_POINTS)
            swing_lows = df[df['swing_low']]['swing_low_value'].dropna().tail(settings.MIN_SWING_POINTS)
            
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                return MarketStructure.UNKNOWN
            
            # Check for Higher Highs
            hh = all(swing_highs.iloc[i] > swing_highs.iloc[i-1] 
                    for i in range(1, len(swing_highs)))
            
            # Check for Higher Lows
            hl = all(swing_lows.iloc[i] > swing_lows.iloc[i-1] 
                    for i in range(1, len(swing_lows)))
            
            # Check for Lower Highs
            lh = all(swing_highs.iloc[i] < swing_highs.iloc[i-1] 
                    for i in range(1, len(swing_highs)))
            
            # Check for Lower Lows
            ll = all(swing_lows.iloc[i] < swing_lows.iloc[i-1] 
                    for i in range(1, len(swing_lows)))
            
            if hh and hl:
                return MarketStructure.BULLISH
            elif lh and ll:
                return MarketStructure.BEARISH
            else:
                return MarketStructure.RANGING
                
        except Exception as e:
            logger.error(f"Error determining market structure: {e}")
            return MarketStructure.UNKNOWN
    
    def _detect_bos(self, df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Detect Break of Structure.
        BOS = Price breaks previous swing high (bullish) or swing low (bearish)
        
        Args:
            df: DataFrame with swing points
            
        Returns:
            Tuple of (detected, type)
        """
        try:
            current_price = df['close'].iloc[-1]
            
            # Get last swing high and low
            swing_highs = df[df['swing_high']]['swing_high_value'].dropna()
            swing_lows = df[df['swing_low']]['swing_low_value'].dropna()
            
            if len(swing_highs) > 0:
                last_swing_high = swing_highs.iloc[-1]
                if current_price > last_swing_high:
                    return (True, "BULLISH_BOS")
            
            if len(swing_lows) > 0:
                last_swing_low = swing_lows.iloc[-1]
                if current_price < last_swing_low:
                    return (True, "BEARISH_BOS")
            
            return (False, None)
            
        except Exception as e:
            logger.error(f"Error detecting BOS: {e}")
            return (False, None)
    
    def _detect_choch(self, df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Detect Change of Character.
        CHoCH = Market structure shift (bullish to bearish or vice versa)
        
        Args:
            df: DataFrame with swing points
            
        Returns:
            Tuple of (detected, type)
        """
        try:
            # Get recent swing points
            swing_highs = df[df['swing_high']]['swing_high_value'].dropna().tail(3)
            swing_lows = df[df['swing_low']]['swing_low_value'].dropna().tail(3)
            
            if len(swing_highs) < 3 or len(swing_lows) < 3:
                return (False, None)
            
            # CHoCH from bullish to bearish:
            # Previous: HH, HL, then breaks previous HL
            if swing_lows.iloc[-1] < swing_lows.iloc[-2]:
                return (True, "BEARISH_CHOCH")
            
            # CHoCH from bearish to bullish:
            # Previous: LL, LH, then breaks previous LH
            if swing_highs.iloc[-1] > swing_highs.iloc[-2]:
                return (True, "BULLISH_CHOCH")
            
            return (False, None)
            
        except Exception as e:
            logger.error(f"Error detecting CHoCH: {e}")
            return (False, None)
    
    def _identify_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """
        Identify order blocks (institutional entry zones).
        Order Block = Last bullish/bearish candle before strong move
        
        Args:
            df: OHLC DataFrame
            
        Returns:
            List of order block dictionaries
        """
        order_blocks = []
        
        try:
            for i in range(1, len(df) - 1):
                # Bullish Order Block: Last bearish candle before bullish move
                if (df['close'].iloc[i] < df['open'].iloc[i] and  # Bearish candle
                    df['close'].iloc[i+1] > df['open'].iloc[i+1] and  # Next is bullish
                    df['close'].iloc[i+1] > df['high'].iloc[i]):  # Strong move up
                    
                    order_blocks.append({
                        'type': 'BULLISH',
                        'high': df['high'].iloc[i],
                        'low': df['low'].iloc[i],
                        'time': df['time'].iloc[i],
                        'candles_ago': len(df) - i - 1
                    })
                
                # Bearish Order Block: Last bullish candle before bearish move
                if (df['close'].iloc[i] > df['open'].iloc[i] and  # Bullish candle
                    df['close'].iloc[i+1] < df['open'].iloc[i+1] and  # Next is bearish
                    df['close'].iloc[i+1] < df['low'].iloc[i]):  # Strong move down
                    
                    order_blocks.append({
                        'type': 'BEARISH',
                        'high': df['high'].iloc[i],
                        'low': df['low'].iloc[i],
                        'time': df['time'].iloc[i],
                        'candles_ago': len(df) - i - 1
                    })
            
            # Filter by validity period
            valid_order_blocks = [ob for ob in order_blocks 
                                 if ob['candles_ago'] <= settings.ORDER_BLOCK_VALIDITY]
            
            return valid_order_blocks[-5:]  # Return last 5
            
        except Exception as e:
            logger.error(f"Error identifying order blocks: {e}")
            return []
    
    def _identify_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """
        Identify Fair Value Gaps (imbalance/inefficiency).
        FVG = Gap between candle highs/lows indicating institutional activity
        
        Args:
            df: OHLC DataFrame
            
        Returns:
            List of FVG dictionaries
        """
        fvgs = []
        
        try:
            for i in range(1, len(df) - 1):
                # Bullish FVG: Gap between candle 1 high and candle 3 low
                if df['low'].iloc[i+1] > df['high'].iloc[i-1]:
                    gap_size = df['low'].iloc[i+1] - df['high'].iloc[i-1]
                    
                    if gap_size >= settings.FVG_MIN_SIZE * 0.0001:  # Convert points to price
                        fvgs.append({
                            'type': 'BULLISH',
                            'high': df['low'].iloc[i+1],
                            'low': df['high'].iloc[i-1],
                            'size': gap_size,
                            'time': df['time'].iloc[i],
                            'filled': False
                        })
                
                # Bearish FVG: Gap between candle 1 low and candle 3 high
                if df['high'].iloc[i+1] < df['low'].iloc[i-1]:
                    gap_size = df['low'].iloc[i-1] - df['high'].iloc[i+1]
                    
                    if gap_size >= settings.FVG_MIN_SIZE * 0.0001:
                        fvgs.append({
                            'type': 'BEARISH',
                            'high': df['low'].iloc[i-1],
                            'low': df['high'].iloc[i+1],
                            'size': gap_size,
                            'time': df['time'].iloc[i],
                            'filled': False
                        })
            
            return fvgs[-5:]  # Return last 5
            
        except Exception as e:
            logger.error(f"Error identifying FVGs: {e}")
            return []
    
    def _calculate_premium_discount(self, df: pd.DataFrame) -> Tuple[float, float]:
        """
        Calculate premium and discount zones based on recent range.
        Premium = Top 50% of range (sell zone)
        Discount = Bottom 50% of range (buy zone)
        
        Args:
            df: OHLC DataFrame
            
        Returns:
            Tuple of (premium_level, discount_level)
        """
        try:
            # Use last 50 candles for range
            recent_high = df['high'].tail(50).max()
            recent_low = df['low'].tail(50).min()
            
            midpoint = (recent_high + recent_low) / 2
            
            return (midpoint, midpoint)  # Midpoint separates premium/discount
            
        except Exception as e:
            logger.error(f"Error calculating premium/discount: {e}")
            return (0, 0)
    
    def _identify_liquidity_levels(self, df: pd.DataFrame) -> Dict:
        """
        Identify liquidity zones (equal highs/lows, round numbers).
        
        Args:
            df: OHLC DataFrame
            
        Returns:
            Dictionary with buy-side and sell-side liquidity
        """
        try:
            # Get recent swing points
            swing_highs = df[df['swing_high']]['swing_high_value'].dropna().tail(5)
            swing_lows = df[df['swing_low']]['swing_low_value'].dropna().tail(5)
            
            liquidity = {
                'buy_side': list(swing_highs.values) if len(swing_highs) > 0 else [],
                'sell_side': list(swing_lows.values) if len(swing_lows) > 0 else []
            }
            
            return liquidity
            
        except Exception as e:
            logger.error(f"Error identifying liquidity: {e}")
            return {'buy_side': [], 'sell_side': []}
    
    def check_multi_timeframe_alignment(self, 
                                       mtf_data: Dict[str, pd.DataFrame]) -> Tuple[bool, TradeSignal]:
        """
        Check if all timeframes align for trade entry.
        All timeframes must show same directional bias.
        
        Args:
            mtf_data: Dictionary of timeframe DataFrames
            
        Returns:
            Tuple of (aligned, signal)
        """
        try:
            # Analyze all timeframes
            for tf, df in mtf_data.items():
                self.analyze_timeframe(df, tf)
            
            # Check alignment
            structures = [self.market_bias[tf]['structure'] for tf in settings.TIMEFRAMES.keys()]
            
            # All bullish?
            if all(s == MarketStructure.BULLISH for s in structures):
                logger.info("✅ Multi-timeframe BULLISH alignment confirmed")
                return (True, TradeSignal.BUY)
            
            # All bearish?
            if all(s == MarketStructure.BEARISH for s in structures):
                logger.info("✅ Multi-timeframe BEARISH alignment confirmed")
                return (True, TradeSignal.SELL)
            
            logger.info("❌ Multi-timeframe alignment not confirmed")
            logger.info(f"  Structures: {structures}")
            
            return (False, TradeSignal.NONE)
            
        except Exception as e:
            logger.error(f"Error checking MTF alignment: {e}")
            return (False, TradeSignal.NONE)
    
    def generate_trade_signal(self, mtf_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate complete trade signal with entry, SL, and TP.
        
        Args:
            mtf_data: Multi-timeframe data
            
        Returns:
            Dictionary with trade signal details
        """
        try:
            # Check alignment
            aligned, signal = self.check_multi_timeframe_alignment(mtf_data)
            
            if not aligned or signal == TradeSignal.NONE:
                return {'signal': TradeSignal.NONE}
            
            # Get M15 for precise entry
            m15_df = mtf_data['M15']
            current_price = m15_df['close'].iloc[-1]
            
            # Get H1 analysis for order blocks
            h1_analysis = self.market_bias.get('H1', {})
            order_blocks = h1_analysis.get('order_blocks', [])
            
            # Calculate entry based on signal type
            if signal == TradeSignal.BUY:
                # Find nearest bullish order block
                bullish_obs = [ob for ob in order_blocks if ob['type'] == 'BULLISH']
                
                if bullish_obs:
                    entry_zone = bullish_obs[0]
                    entry_price = entry_zone['low']
                    stop_loss = entry_zone['low'] - (settings.SL_BUFFER_POINTS * 0.0001)
                    take_profit = entry_price + ((entry_price - stop_loss) * settings.TP_MULTIPLIER)
                else:
                    # Use current price with buffer
                    entry_price = current_price
                    stop_loss = current_price - (100 * 0.0001)  # 100 points
                    take_profit = current_price + (200 * 0.0001)  # 200 points (1:2 RR)
            
            else:  # SELL
                # Find nearest bearish order block
                bearish_obs = [ob for ob in order_blocks if ob['type'] == 'BEARISH']
                
                if bearish_obs:
                    entry_zone = bearish_obs[0]
                    entry_price = entry_zone['high']
                    stop_loss = entry_zone['high'] + (settings.SL_BUFFER_POINTS * 0.0001)
                    take_profit = entry_price - ((stop_loss - entry_price) * settings.TP_MULTIPLIER)
                else:
                    # Use current price with buffer
                    entry_price = current_price
                    stop_loss = current_price + (100 * 0.0001)
                    take_profit = current_price - (200 * 0.0001)
            
            return {
                'signal': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'current_price': current_price,
                'analysis': self.market_bias
            }
            
        except Exception as e:
            logger.error(f"Error generating trade signal: {e}")
            return {'signal': TradeSignal.NONE}
