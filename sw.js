// 첫직관 서비스 워커: 언제나 인터넷에서 먼저 받고, 안 될 때만(경기장에서 신호가 약할 때) 저장해 둔 것을 씀
// 일정이 매일 바뀌어서 저장본을 먼저 쓰면 옛 일정이 보임. 그래서 순서를 인터넷 → 저장본으로 둠
const CACHE='first-gikgwan-v1';
const CORE=['./','index.html','manifest.json','icons/icon.svg','icons/icon-192.png',
  'fonts/KBO-Dia-Gothic_medium.woff','fonts/KBO-Dia-Gothic_bold.woff',
  ...['baseball','volleyball','basketball','hockey','handball','soccer','esports'].map(id=>`data/${id}.js`)];

self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  const req=e.request,url=new URL(req.url);
  if(req.method!=='GET'||url.origin!==location.origin)return;   // 다른 사이트(글꼴 CDN, 영상 썸네일)는 브라우저에 맡김
  // 데이터 주소 뒤의 ?v=(1분마다 바뀌는 번호)는 빼고 저장해서 한 파일에 한 저장본만 남김
  const key=url.origin+url.pathname;
  e.respondWith(fetch(req).then(res=>{
    if(res.ok){const copy=res.clone();caches.open(CACHE).then(c=>c.put(key,copy))}
    return res;
  }).catch(()=>caches.match(key).then(r=>r||(req.mode==='navigate'?caches.match('index.html'):Response.error()))));
});
