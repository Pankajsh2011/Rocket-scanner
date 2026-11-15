/**
 * ═════════════════════════════════════════════════════════════════════
 *  GOOGLE ADMOB MONETIZATION CONTROLLER FOR GROK BOT INDIA SCREENER
 *  Supports Banner Ads, Interstitial Ads, and Rewarded Video Ads
 * ═════════════════════════════════════════════════════════════════════
 */

const AdMobConfig = {
  // Set to false when publishing to Google Play Store / Apple App Store!
  isTesting: true,

  // Google's Official Test Ad Unit IDs (Guaranteed to work and won't ban your account)
  testIds: {
    bannerAndroid: 'ca-app-pub-3940256099942544/6300978111',
    interstitialAndroid: 'ca-app-pub-3940256099942544/1033173712',
    rewardedAndroid: 'ca-app-pub-3940256099942544/5224354917',
    bannerIos: 'ca-app-pub-3940256099942544/2934735716',
    interstitialIos: 'ca-app-pub-3940256099942544/4411468910',
    rewardedIos: 'ca-app-pub-3940256099942544/1712485313'
  },

  // ── PASTE YOUR REAL GOOGLE ADMOB AD UNIT IDS HERE BEFORE PLAY STORE RELEASE ──
  liveIds: {
    bannerAndroid: 'ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY',
    interstitialAndroid: 'ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY',
    rewardedAndroid: 'ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY',
    bannerIos: 'ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY',
    interstitialIos: 'ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY',
    rewardedIos: 'ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY'
  }
};

class AdMobManager {
  constructor() {
    this.isNative = typeof window.Capacitor !== 'undefined' && window.Capacitor.isNativePlatform();
    this.scanCount = 0;
    this.isVipUnlocked = localStorage.getItem('grok_vip_unlocked') === 'true';
    this.init();
  }

  async init() {
    console.log('[AdMob] Initializing AdMob Manager... IsNative:', this.isNative);
    if (this.isNative && window.Capacitor.Plugins.AdMob) {
      try {
        const { AdMob } = window.Capacitor.Plugins;
        await AdMob.initialize({
          testingDevices: ['2077ef9a63d2b398840261c8221a0c9b'],
          initializeForTesting: AdMobConfig.isTesting
        });
        console.log('[AdMob] AdMob initialized successfully');
        this.showBanner();
      } catch (e) {
        console.warn('[AdMob] Native AdMob init error:', e);
      }
    } else {
      this.renderWebFallbackBanner();
    }
  }

  getAdId(type) {
    const isAndroid = this.isNative && window.Capacitor.getPlatform() === 'android';
    const dict = AdMobConfig.isTesting ? AdMobConfig.testIds : AdMobConfig.liveIds;
    if (type === 'banner') return isAndroid ? dict.bannerAndroid : dict.bannerIos;
    if (type === 'interstitial') return isAndroid ? dict.interstitialAndroid : dict.interstitialIos;
    if (type === 'rewarded') return isAndroid ? dict.rewardedAndroid : dict.rewardedIos;
    return dict.bannerAndroid;
  }

  // ── 1. BOTTOM BANNER AD ──
  async showBanner() {
    if (this.isNative && window.Capacitor.Plugins.AdMob) {
      try {
        const { AdMob, BannerAdSize, BannerAdPosition } = window.Capacitor.Plugins;
        await AdMob.showBanner({
          adId: this.getAdId('banner'),
          adSize: BannerAdSize.ADAPTIVE_BANNER,
          position: BannerAdPosition.BOTTOM_CENTER,
          margin: 0,
          isTesting: AdMobConfig.isTesting
        });
        console.log('[AdMob] Banner ad displayed');
      } catch (e) {
        console.warn('[AdMob] Banner error:', e);
      }
    }
  }

  // ── 2. INTERSTITIAL AD (Shown every 3 scans) ──
  async showInterstitial() {
    this.scanCount++;
    console.log(`[AdMob] Scan count: ${this.scanCount}`);
    if (this.scanCount % 3 !== 0) return; // Show every 3rd scan

    if (this.isNative && window.Capacitor.Plugins.AdMob) {
      try {
        const { AdMob } = window.Capacitor.Plugins;
        await AdMob.prepareInterstitial({
          adId: this.getAdId('interstitial'),
          isTesting: AdMobConfig.isTesting
        });
        await AdMob.showInterstitial();
        console.log('[AdMob] Interstitial shown');
      } catch (e) {
        console.warn('[AdMob] Interstitial error:', e);
      }
    } else {
      console.log('[AdMob Web] Interstitial trigger: 3rd scan reached');
    }
  }

  // ── 3. REWARDED VIDEO AD (Unlock VIP 20%+ Circuit Rockets) ──
  async showRewardedAd(onRewardGranted) {
    if (this.isNative && window.Capacitor.Plugins.AdMob) {
      try {
        const { AdMob, RewardAdPluginEvents } = window.Capacitor.Plugins;
        
        AdMob.addListener(RewardAdPluginEvents.Rewarded, (reward) => {
          console.log('[AdMob] User earned reward:', reward);
          this.isVipUnlocked = true;
          localStorage.setItem('grok_vip_unlocked', 'true');
          if (onRewardGranted) onRewardGranted();
        });

        await AdMob.prepareRewardVideoAd({
          adId: this.getAdId('rewarded'),
          isTesting: AdMobConfig.isTesting
        });
        await AdMob.showRewardVideoAd();
      } catch (e) {
        console.warn('[AdMob] Rewarded Ad error:', e);
        // Fallback for testing
        this.isVipUnlocked = true;
        localStorage.setItem('grok_vip_unlocked', 'true');
        if (onRewardGranted) onRewardGranted();
      }
    } else {
      // Browser test simulator
      const confirmAd = confirm("🎬 [Google AdMob Rewarded Video Ad]\n\nWatch this 15-second sponsor video to unlock 20%+ Circuit Rockets VIP Scanner for 24 hours?\n\n(Click OK to simulate ad completion)");
      if (confirmAd) {
        this.isVipUnlocked = true;
        localStorage.setItem('grok_vip_unlocked', 'true');
        alert("✅ Reward Granted! VIP 20%+ Circuit Rockets Scanner is now fully unlocked.");
        if (onRewardGranted) onRewardGranted();
      }
    }
  }

  // ── 4. WEB FALLBACK BANNER ──
  renderWebFallbackBanner() {
    let container = document.getElementById('admob-web-banner');
    if (!container) {
      container = document.createElement('div');
      container.id = 'admob-web-banner';
      container.style.cssText = `
        position: fixed; bottom: 0; left: 0; right: 0; height: 50px;
        background: #181d28; border-top: 1px solid #28344e;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 16px; z-index: 999; font-family: sans-serif;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
      `;
      container.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:0.65rem;background:#ff9800;color:#000;font-weight:700;padding:1px 5px;border-radius:3px;">Ad</span>
          <span style="font-size:0.75rem;color:#cfd8dc;">Google AdMob Banner · High eCPM Finance Ads Powered</span>
        </div>
        <button onclick="window.adMob.showRewardedAd()" style="background:#ff4b2b;color:#fff;border:none;padding:5px 12px;border-radius:4px;font-size:0.72rem;font-weight:700;cursor:pointer;">
          🎬 Unlock 20%+ VIP
        </button>
      `;
      document.body.appendChild(container);
      document.body.style.paddingBottom = '55px';
    }
  }
}

// Global instance
window.adMob = new AdMobManager();
