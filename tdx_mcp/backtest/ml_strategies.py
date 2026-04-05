# coding=utf-8
"""
机器学习策略模块
功能：
1. LSTM时序预测策略
2. Random Forest分类策略
3. XGBoost回归策略
4. 特征工程
5. 模型训练和保存
"""
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import os
from .strategy_base import BaseStrategy

# 机器学习库检测
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class FeatureEngineer:
    """
    特征工程类
    
    生成技术指标特征用于机器学习
    """
    
    @staticmethod
    def create_features(data: pd.DataFrame, include_target: bool = True) -> pd.DataFrame:
        """
        创建特征
        
        Args:
            data: 股票数据（必须包含OHLCV）
            include_target: 是否包含目标变量
        
        Returns:
            包含特征的DataFrame
        """
        df = data.copy()
        
        # 价格特征
        df['return_1d'] = df['close'].pct_change()
        df['return_5d'] = df['close'].pct_change(5)
        df['return_10d'] = df['close'].pct_change(10)
        
        # 波动率特征
        df['volatility_5d'] = df['return_1d'].rolling(5).std()
        df['volatility_10d'] = df['return_1d'].rolling(10).std()
        df['volatility_20d'] = df['return_1d'].rolling(20).std()
        
        # 均线特征
        df['ma_5'] = df['close'].rolling(5).mean()
        df['ma_10'] = df['close'].rolling(10).mean()
        df['ma_20'] = df['close'].rolling(20).mean()
        df['ma_60'] = df['close'].rolling(60).mean()
        
        # 均线偏离度
        df['bias_5'] = (df['close'] - df['ma_5']) / df['ma_5']
        df['bias_10'] = (df['close'] - df['ma_10']) / df['ma_10']
        df['bias_20'] = (df['close'] - df['ma_20']) / df['ma_20']
        
        # 技术指标
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 布林带
        df['boll_middle'] = df['close'].rolling(20).mean()
        df['boll_std'] = df['close'].rolling(20).std()
        df['boll_upper'] = df['boll_middle'] + 2 * df['boll_std']
        df['boll_lower'] = df['boll_middle'] - 2 * df['boll_std']
        df['boll_pct'] = (df['close'] - df['boll_lower']) / (df['boll_upper'] - df['boll_lower'])
        
        # 成交量特征
        df['volume_ma_5'] = df['volume'].rolling(5).mean()
        df['volume_ma_10'] = df['volume'].rolling(10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_5']
        
        # 价格形态
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['body'] = abs(df['close'] - df['open'])
        
        # 目标变量（未来N日收益率）
        if include_target:
            df['target_1d'] = df['close'].shift(-1) / df['close'] - 1
            df['target_5d'] = df['close'].shift(-5) / df['close'] - 1
            df['target_direction'] = (df['target_1d'] > 0).astype(int)  # 1:涨 0:跌
        
        return df
    
    @staticmethod
    def prepare_ml_data(
        data: pd.DataFrame,
        feature_columns: List[str] = None,
        target_column: str = 'target_direction',
        look_back: int = 0,
        test_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        准备机器学习数据
        
        Args:
            data: 包含特征的DataFrame
            feature_columns: 特征列名
            target_column: 目标列名
            look_back: 回看窗口（用于LSTM）
            test_size: 测试集比例
        
        Returns:
            (X_train, X_test, y_train, y_test)
        """
        # 默认特征列
        if feature_columns is None:
            feature_columns = [
                'return_1d', 'return_5d', 'return_10d',
                'volatility_5d', 'volatility_10d',
                'bias_5', 'bias_10', 'bias_20',
                'rsi_14', 'macd_hist', 'boll_pct',
                'volume_ratio'
            ]
        
        # 提取特征和目标
        df = data.dropna(subset=feature_columns + [target_column])
        
        X = df[feature_columns].values
        y = df[target_column].values
        
        # 标准化（如果sklearn可用）
        if SKLEARN_AVAILABLE:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
        else:
            # 手动标准化
            X_scaled = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
        
        # 如果是LSTM，需要reshape
        if look_back > 0:
            X_lstm = []
            y_lstm = []
            for i in range(look_back, len(X_scaled)):
                X_lstm.append(X_scaled[i-look_back:i])
                y_lstm.append(y[i])
            X_scaled = np.array(X_lstm)
            y = np.array(y_lstm)
        
        # 分割训练集和测试集
        split_idx = int(len(X_scaled) * (1 - test_size))
        
        X_train = X_scaled[:split_idx]
        X_test = X_scaled[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        return X_train, X_test, y_train, y_test


class LSTMStrategy(BaseStrategy):
    """
    LSTM时序预测策略
    
    使用长短期记忆网络预测股价走势
    
    参数：
    - look_back: 回看窗口（默认20）
    - epochs: 训练轮数（默认50）
    - batch_size: 批大小（默认32）
    - units: LSTM单元数（默认50）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'look_back': 20,
            'epochs': 50,
            'batch_size': 32,
            'units': 50,
            'dropout': 0.2,
            'learning_rate': 0.001
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        # 检查TensorFlow是否可用
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow未安装，请运行: pip install tensorflow")
        
        self.model = None
        self.scaler = None
        self.is_trained = False
    
    def get_name(self) -> str:
        return "LSTM策略"
    
    def build_model(self, input_shape: Tuple[int, int]) -> Any:
        """
        构建LSTM模型
        
        Args:
            input_shape: 输入形状 (look_back, features)
        
        Returns:
            Keras模型
        """
        model = Sequential([
            LSTM(self.params['units'], return_sequences=True, input_shape=input_shape),
            Dropout(self.params['dropout']),
            LSTM(self.params['units'] // 2),
            Dropout(self.params['dropout']),
            Dense(1, activation='sigmoid')
        ])
        
        optimizer = keras.optimizers.Adam(learning_rate=self.params['learning_rate'])
        model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
        
        return model
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        训练模型
        
        Args:
            data: 训练数据
        
        Returns:
            训练结果
        """
        # 创建特征
        df = FeatureEngineer.create_features(data)
        
        # 准备数据
        look_back = self.params['look_back']
        X_train, X_test, y_train, y_test = FeatureEngineer.prepare_ml_data(
            df, look_back=look_back
        )
        
        # 构建模型
        input_shape = (look_back, X_train.shape[2])
        self.model = self.build_model(input_shape)
        
        # 训练
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        history = self.model.fit(
            X_train, y_train,
            epochs=self.params['epochs'],
            batch_size=self.params['batch_size'],
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        # 评估
        loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        self.is_trained = True
        
        return {
            'train_loss': history.history['loss'][-1],
            'train_accuracy': history.history['accuracy'][-1],
            'val_loss': history.history['val_loss'][-1],
            'val_accuracy': history.history['val_accuracy'][-1],
            'test_accuracy': accuracy
        }
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        预测
        
        Args:
            data: 待预测数据
        
        Returns:
            预测结果 (概率)
        """
        if not self.is_trained:
            raise ValueError("模型未训练，请先调用train()")
        
        # 创建特征
        df = FeatureEngineer.create_features(data)
        
        # 准备数据
        look_back = self.params['look_back']
        X, _, _, _ = FeatureEngineer.prepare_ml_data(df, look_back=look_back, test_size=0)
        
        # 预测
        predictions = self.model.predict(X, verbose=0)
        
        return predictions.flatten()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            data: 股票数据
        
        Returns:
            包含信号的DataFrame
        """
        df = data.copy()
        
        # 如果未训练，先训练
        if not self.is_trained:
            self.train(df)
        
        # 预测
        predictions = self.predict(df)
        
        # 对齐索引
        look_back = self.params['look_back']
        signal_index = df.index[look_back:look_back+len(predictions)]
        
        # 生成信号
        df['signal'] = 0
        df.loc[signal_index, 'ml_prob'] = predictions
        
        # 买入：概率>0.6
        df.loc[signal_index[predictions > 0.6], 'signal'] = 1
        
        # 卖出：概率<0.4
        df.loc[signal_index[predictions < 0.4], 'signal'] = -1
        
        return df
    
    def save_model(self, filepath: str):
        """保存模型"""
        if self.model:
            self.model.save(filepath)
    
    def load_model(self, filepath: str):
        """加载模型"""
        self.model = load_model(filepath)
        self.is_trained = True


class RandomForestStrategy(BaseStrategy):
    """
    随机森林策略
    
    使用随机森林分类预测涨跌
    
    参数：
    - n_estimators: 树的数量（默认100）
    - max_depth: 最大深度（默认10）
    - min_samples_split: 分裂最小样本数（默认5）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn未安装，请运行: pip install scikit-learn")
        
        self.model = None
        self.is_trained = False
        self.feature_importance = None
    
    def get_name(self) -> str:
        return "随机森林策略"
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """训练模型"""
        # 创建特征
        df = FeatureEngineer.create_features(data)
        
        # 准备数据
        X_train, X_test, y_train, y_test = FeatureEngineer.prepare_ml_data(df)
        
        # 构建模型
        self.model = RandomForestClassifier(
            n_estimators=self.params['n_estimators'],
            max_depth=self.params['max_depth'],
            min_samples_split=self.params['min_samples_split'],
            min_samples_leaf=self.params['min_samples_leaf'],
            random_state=self.params['random_state'],
            n_jobs=-1
        )
        
        # 训练
        self.model.fit(X_train, y_train)
        
        # 评估
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        
        # 特征重要性
        feature_columns = [
            'return_1d', 'return_5d', 'return_10d',
            'volatility_5d', 'volatility_10d',
            'bias_5', 'bias_10', 'bias_20',
            'rsi_14', 'macd_hist', 'boll_pct',
            'volume_ratio'
        ]
        
        self.feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
        
        self.is_trained = True
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'feature_importance': self.feature_importance
        }
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_trained:
            raise ValueError("模型未训练")
        
        # 创建特征
        df = FeatureEngineer.create_features(data)
        
        # 提取特征
        feature_columns = [
            'return_1d', 'return_5d', 'return_10d',
            'volatility_5d', 'volatility_10d',
            'bias_5', 'bias_10', 'bias_20',
            'rsi_14', 'macd_hist', 'boll_pct',
            'volume_ratio'
        ]
        
        X = df[feature_columns].dropna().values
        
        # 预测概率
        predictions = self.model.predict_proba(X)[:, 1]
        
        return predictions
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        df = data.copy()
        
        # 如果未训练，先训练
        if not self.is_trained:
            self.train(df)
        
        # 预测
        predictions = self.predict(df)
        
        # 对齐索引
        feature_columns = [
            'return_1d', 'return_5d', 'return_10d',
            'volatility_5d', 'volatility_10d',
            'bias_5', 'bias_10', 'bias_20',
            'rsi_14', 'macd_hist', 'boll_pct',
            'volume_ratio'
        ]
        
        valid_index = df[feature_columns].dropna().index
        signal_index = valid_index[:len(predictions)]
        
        # 生成信号
        df['signal'] = 0
        df.loc[signal_index, 'ml_prob'] = predictions
        
        # 买入：概率>0.55
        df.loc[signal_index[predictions > 0.55], 'signal'] = 1
        
        # 卖出：概率<0.45
        df.loc[signal_index[predictions < 0.45], 'signal'] = -1
        
        return df
    
    def save_model(self, filepath: str):
        """保存模型"""
        if self.model:
            with open(filepath, 'wb') as f:
                pickle.dump(self.model, f)
    
    def load_model(self, filepath: str):
        """加载模型"""
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        self.is_trained = True


class XGBoostStrategy(BaseStrategy):
    """
    XGBoost策略
    
    使用XGBoost进行回归预测
    
    参数：
    - n_estimators: 树的数量（默认100）
    - max_depth: 最大深度（默认6）
    - learning_rate: 学习率（默认0.1）
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        if params:
            default_params.update(params)
        
        super().__init__(default_params)
        
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost未安装，请运行: pip install xgboost")
        
        self.model = None
        self.is_trained = False
    
    def get_name(self) -> str:
        return "XGBoost策略"
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """训练模型"""
        # 创建特征
        df = FeatureEngineer.create_features(data)
        
        # 准备数据（使用目标收益率）
        target_column = 'target_1d'
        feature_columns = [
            'return_1d', 'return_5d', 'return_10d',
            'volatility_5d', 'volatility_10d',
            'bias_5', 'bias_10', 'bias_20',
            'rsi_14', 'macd_hist', 'boll_pct',
            'volume_ratio'
        ]
        
        X_train, X_test, y_train, y_test = FeatureEngineer.prepare_ml_data(
            df, feature_columns, target_column, test_size=0.2
        )
        
        # 构建模型
        self.model = xgb.XGBRegressor(
            n_estimators=self.params['n_estimators'],
            max_depth=self.params['max_depth'],
            learning_rate=self.params['learning_rate'],
            subsample=self.params['subsample'],
            colsample_bytree=self.params['colsample_bytree'],
            random_state=self.params['random_state']
        )
        
        # 训练
        self.model.fit(X_train, y_train)
        
        # 评估
        y_pred = self.model.predict(X_test)
        mse = np.mean((y_test - y_pred) ** 2)
        mae = np.mean(np.abs(y_test - y_pred))
        
        # 方向准确率
        direction_accuracy = np.mean(np.sign(y_test) == np.sign(y_pred))
        
        self.is_trained = True
        
        return {
            'mse': mse,
            'mae': mae,
            'direction_accuracy': direction_accuracy
        }
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_trained:
            raise ValueError("模型未训练")
        
        # 创建特征
        df = FeatureEngineer.create_features(data)
        
        # 提取特征
        feature_columns = [
            'return_1d', 'return_5d', 'return_10d',
            'volatility_5d', 'volatility_10d',
            'bias_5', 'bias_10', 'bias_20',
            'rsi_14', 'macd_hist', 'boll_pct',
            'volume_ratio'
        ]
        
        X = df[feature_columns].dropna().values
        
        # 预测收益率
        predictions = self.model.predict(X)
        
        return predictions
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        df = data.copy()
        
        # 如果未训练，先训练
        if not self.is_trained:
            self.train(df)
        
        # 预测
        predictions = self.predict(df)
        
        # 对齐索引
        feature_columns = [
            'return_1d', 'return_5d', 'return_10d',
            'volatility_5d', 'volatility_10d',
            'bias_5', 'bias_10', 'bias_20',
            'rsi_14', 'macd_hist', 'boll_pct',
            'volume_ratio'
        ]
        
        valid_index = df[feature_columns].dropna().index
        signal_index = valid_index[:len(predictions)]
        
        # 生成信号
        df['signal'] = 0
        df.loc[signal_index, 'ml_prediction'] = predictions
        
        # 买入：预测收益率>0.01
        df.loc[signal_index[predictions > 0.01], 'signal'] = 1
        
        # 卖出：预测收益率<-0.01
        df.loc[signal_index[predictions < -0.01], 'signal'] = -1
        
        return df
    
    def save_model(self, filepath: str):
        """保存模型"""
        if self.model:
            self.model.save_model(filepath)
    
    def load_model(self, filepath: str):
        """加载模型"""
        self.model = xgb.XGBRegressor()
        self.model.load_model(filepath)
        self.is_trained = True


# 导出策略类
__all__ = [
    'FeatureEngineer',
    'LSTMStrategy',
    'RandomForestStrategy',
    'XGBoostStrategy'
]
