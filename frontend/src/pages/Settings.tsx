import React, { useState, useEffect } from 'react';
import { GlassCard } from '../components/GlassCard';
import { apiService } from '../services/api';
import { RiskSettings } from '../types';
import { Save, RefreshCw, CheckCircle, Sliders, Server, Wifi } from 'lucide-react';

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<RiskSettings>({
    RISK_THRESHOLD_LOW: 0,
    RISK_THRESHOLD_MEDIUM: 30,
    RISK_THRESHOLD_HIGH: 60,
    RISK_THRESHOLD_CRITICAL: 80,
    SCORE_CUSTOMER_ENTERED: 0,
    SCORE_SHELF_INTERACTION: 5,
    SCORE_PRODUCT_PICKED: 10,
    SCORE_PRODUCT_IN_BASKET: -10,
    SCORE_PRODUCT_RETURNED: -5,
    SCORE_PRODUCT_UNRESOLVED: 25,
    SCORE_SUSPICIOUS_BEHAVIOR: 30,
    SCORE_POSSIBLE_CONCEALMENT: 45,
    SCORE_HIGH_RISK_DETECTED: 50,
    SCORE_LONG_DWELL_TIME: 10,
    SCORE_UNUSUAL_ZONE_TRANSITION: 15,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const data = await apiService.getSettings();
      if (data) {
        setSettings(data);
      }
    } catch (err) {
      console.error('Failed to fetch settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSettings((prev) => ({
      ...prev,
      [name]: parseFloat(value) || 0,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await apiService.updateSettings(settings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center space-x-2">
            <Sliders className="w-7 h-7 text-cyan-400" />
            <span>Risk Engine Settings</span>
          </h1>
          <p className="text-sm text-slate-400">Configure multi-signal risk thresholds and scoring deltas</p>
        </div>
        <button
          onClick={fetchSettings}
          disabled={loading}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-2 border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Reload Config</span>
        </button>
      </div>

      {saveSuccess && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center space-x-3 text-emerald-400 text-sm">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <span>Settings saved successfully. Multi-signal risk engine updated.</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Risk Thresholds */}
        <GlassCard title="Risk Level Boundaries">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Low Threshold</label>
              <input
                type="number"
                name="RISK_THRESHOLD_LOW"
                value={settings.RISK_THRESHOLD_LOW}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Medium Threshold</label>
              <input
                type="number"
                name="RISK_THRESHOLD_MEDIUM"
                value={settings.RISK_THRESHOLD_MEDIUM}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">High Threshold</label>
              <input
                type="number"
                name="RISK_THRESHOLD_HIGH"
                value={settings.RISK_THRESHOLD_HIGH}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Critical Threshold</label>
              <input
                type="number"
                name="RISK_THRESHOLD_CRITICAL"
                value={settings.RISK_THRESHOLD_CRITICAL}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>
        </GlassCard>

        {/* Scoring Deltas */}
        <GlassCard title="Scoring Deltas per Event Type">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Shelf Interaction Delta</label>
              <input
                type="number"
                name="SCORE_SHELF_INTERACTION"
                value={settings.SCORE_SHELF_INTERACTION}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Product Picked Delta</label>
              <input
                type="number"
                name="SCORE_PRODUCT_PICKED"
                value={settings.SCORE_PRODUCT_PICKED}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Product in Basket Delta</label>
              <input
                type="number"
                name="SCORE_PRODUCT_IN_BASKET"
                value={settings.SCORE_PRODUCT_IN_BASKET}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Product Unresolved Delta</label>
              <input
                type="number"
                name="SCORE_PRODUCT_UNRESOLVED"
                value={settings.SCORE_PRODUCT_UNRESOLVED}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Suspicious Behavior Delta</label>
              <input
                type="number"
                name="SCORE_SUSPICIOUS_BEHAVIOR"
                value={settings.SCORE_SUSPICIOUS_BEHAVIOR}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Long Dwell Time Delta</label>
              <input
                type="number"
                name="SCORE_LONG_DWELL_TIME"
                value={settings.SCORE_LONG_DWELL_TIME || 10}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Unusual Zone Transition Delta</label>
              <input
                type="number"
                name="SCORE_UNUSUAL_ZONE_TRANSITION"
                value={settings.SCORE_UNUSUAL_ZONE_TRANSITION || 15}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Possible Concealment Delta</label>
              <input
                type="number"
                name="SCORE_POSSIBLE_CONCEALMENT"
                value={settings.SCORE_POSSIBLE_CONCEALMENT}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>
        </GlassCard>

        {/* System Server Info */}
        <GlassCard title="Telemetry Server & WebSocket Status">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center space-x-3">
              <Server className="w-5 h-5 text-cyan-400" />
              <div>
                <span className="font-bold text-slate-200">Backend API URL</span>
                <p className="text-slate-400 font-mono">http://127.0.0.1:8002/api</p>
              </div>
            </div>
            <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 flex items-center space-x-3">
              <Wifi className="w-5 h-5 text-emerald-400" />
              <div>
                <span className="font-bold text-slate-200">WebSocket Endpoint</span>
                <p className="text-slate-400 font-mono">ws://127.0.0.1:8002/ws/dashboard</p>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-cyan-500/20 flex items-center space-x-2 transition-all"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
