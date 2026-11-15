with open(r'C:\Users\Dell\india-screener\templates\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add manifest and admob-manager.js in head
head_insert = '''<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#101522">
<script src="admob-manager.js"></script>'''

content = content.replace('</head>', f'{head_insert}\n</head>')

# Add API_BASE resolution to script
api_base_insert = '''// Dynamic API Base URL for Mobile WebView & Web
const API_BASE = (window.location.protocol.startsWith('http') && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')
  ? window.location.origin
  : (localStorage.getItem('grok_api_base') || 'http://localhost:5050');

console.log('[App] Screener API Base:', API_BASE);
function setBackendUrl() {
  const current = localStorage.getItem('grok_api_base') || API_BASE;
  const newUrl = prompt('Enter Screener Backend Server URL:\\n(e.g. http://192.168.1.100:5050 or https://your-server.zeabur.app)', current);
  if (newUrl && newUrl.trim() !== '') {
    localStorage.setItem('grok_api_base', newUrl.trim());
    window.location.reload();
  }
}
'''

content = content.replace('<script>\nconst socket = io();', f'<script>\n{api_base_insert}\nconst socket = (typeof io !== "undefined") ? io(API_BASE, {{ reconnectionDelay: 1000, timeout: 5000 }}) : null;')

# Add AdMob hooks in triggerScan and quickScan20Rockets
content = content.replace('function triggerScan(forceMinRet = null) {', '''function triggerScan(forceMinRet = null) {
  if (window.adMob && typeof window.adMob.showInterstitial === 'function') {
    window.adMob.showInterstitial();
  }''')

content = content.replace('function quickScan20Rockets() {', '''function quickScan20Rockets() {
  if (window.adMob && !window.adMob.isVipUnlocked) {
    window.adMob.showRewardedAd(() => { triggerScan(20); });
    return;
  }''')

# Replace fetch calls with API_BASE prefix
content = content.replace("fetch('/api/", "fetch(API_BASE + '/api/")
content = content.replace("fetch(`/api/", "fetch(`${API_BASE}/api/")

with open(r'C:\Users\Dell\india-screener\mobile-app\www\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('mobile-app/www/index.html updated successfully!')
