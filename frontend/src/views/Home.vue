<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'

const projectMapRef = ref<HTMLElement | null>(null)
const projectScaleRef = ref<HTMLElement | null>(null)
const buildMethodRef = ref<HTMLElement | null>(null)
const assetSectionRef = ref<HTMLElement | null>(null)
const baiduMapRef = ref<HTMLElement | null>(null)
const baiduMapStatus = ref('')
const showBackTop = ref(false)
const BAIDU_MAP_AK = import.meta.env.VITE_BAIDU_MAP_AK || ''
const BAIDU_MAP_SCRIPT_ID = 'baidu-map-gl-script'

declare global {
  interface Window {
    BMapGL?: any
    initCapsuleCabinMap?: () => void
  }
}

const scrollToSection = (target: HTMLElement | null) => {
  target?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  })
}

const updateBackTopVisibility = () => {
  showBackTop.value = window.scrollY > 520
}

const renderBaiduMap = () => {
  if (!baiduMapRef.value || !window.BMapGL) return

  const BMapGL = window.BMapGL
  const map = new BMapGL.Map(baiduMapRef.value)
  const fallbackPoint = new BMapGL.Point(122.12042, 37.51307)

  map.centerAndZoom(fallbackPoint, 13)
  map.enableScrollWheelZoom(true)
  map.addControl(new BMapGL.ZoomControl())
  map.addControl(new BMapGL.ScaleControl())

  const setMarker = (point: any, title = '威海滨海度假区') => {
    map.centerAndZoom(point, 15)
    const marker = new BMapGL.Marker(point)
    map.clearOverlays()
    map.addOverlay(marker)

    const label = new BMapGL.Label(title, {
      position: point,
      offset: new BMapGL.Size(16, -34),
    })
    label.setStyle({
      color: '#083344',
      border: '1px solid rgba(15, 118, 110, 0.28)',
      borderRadius: '8px',
      padding: '7px 10px',
      fontSize: '13px',
      fontWeight: '700',
      backgroundColor: 'rgba(255, 255, 255, 0.92)',
      boxShadow: '0 8px 20px rgba(15, 23, 42, 0.12)',
    })
    map.addOverlay(label)
  }

  const geocoder = new BMapGL.Geocoder()
  geocoder.getPoint(
    '威海滨海度假区',
    (point: any) => {
      setMarker(point || fallbackPoint)
      baiduMapStatus.value = ''
    },
    '威海市'
  )
}

const loadBaiduMap = () => {
  if (!BAIDU_MAP_AK) {
    baiduMapStatus.value = '未配置百度地图 AK，无法加载动态地图。'
    return
  }

  if (window.BMapGL) {
    renderBaiduMap()
    return
  }

  const existingScript = document.getElementById(BAIDU_MAP_SCRIPT_ID)
  if (existingScript) return

  baiduMapStatus.value = '百度地图加载中...'
  window.initCapsuleCabinMap = renderBaiduMap

  const script = document.createElement('script')
  script.id = BAIDU_MAP_SCRIPT_ID
  script.src = `https://api.map.baidu.com/api?v=1.0&type=webgl&ak=${encodeURIComponent(BAIDU_MAP_AK)}&callback=initCapsuleCabinMap`
  script.async = true
  script.onerror = () => {
    baiduMapStatus.value = '百度地图加载失败，请检查 AK、域名白名单或网络访问。'
  }
  document.head.appendChild(script)
}

onMounted(() => {
  const shouldRestoreScroll = sessionStorage.getItem('home_restore_scroll') === '1'
  const savedHomeY = Number(sessionStorage.getItem('home_scroll_y') || 0)
  sessionStorage.removeItem('home_restore_scroll')

  const scrollTarget = shouldRestoreScroll ? savedHomeY : 0
  const applyScrollTarget = () => window.scrollTo(0, scrollTarget)

  applyScrollTarget()
  requestAnimationFrame(applyScrollTarget)
  setTimeout(applyScrollTarget, 120)
  setTimeout(applyScrollTarget, 500)

  if (!shouldRestoreScroll) {
    const startedAt = Date.now()
    const keepTopTimer = window.setInterval(() => {
      applyScrollTarget()
      if (Date.now() - startedAt > 1600) {
        window.clearInterval(keepTopTimer)
      }
    }, 80)
  } else {
    setTimeout(applyScrollTarget, 900)
  }

  updateBackTopVisibility()
  window.addEventListener('scroll', updateBackTopVisibility, { passive: true })
  loadBaiduMap()
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateBackTopVisibility)
})

onBeforeRouteLeave(() => {
  sessionStorage.setItem('home_scroll_y', String(window.scrollY))
})
</script>

<template>
  <main class="home-page">
    <section class="hero">
      <div class="mobile-hero-image" aria-hidden="true"></div>

      <div class="hero-content">
        <p class="eyebrow">回溯式 AI PoC｜基于已建成项目再建模</p>
        <h1>瑞泽·海度假民宿</h1>
        <h2>AI 配置与交付规划 Agent</h2>
        <h3>从真实民宿案例到可演示的 AI Agent 闭环</h3>
        <p class="lead">
          本项目将已建成民宿的产品规格、户型信息、空间配置与装配式交付流程，抽象为可执行的 Agent 工作流。用户输入扩建需求后，系统生成配置建议、BOM 控制与交付任务规划，用于验证 AI 在需求收集、配置辅助与交付协同中的产品价值。
        </p>
        <div class="hero-actions">
          <a-button type="primary" size="large" @click="$router.push('/chat')">进入 Agent 规划台</a-button>
          <a-button class="ghost-btn" size="large" @click="$router.push({ path: '/project/demo-capsule-cabin', query: { source: 'home-poc' } })">查看 PoC 方案</a-button>
        </div>
      </div>

      <section class="case-strip">
        <button
          type="button"
          class="case-location"
          title="查看页面内项目位置地图"
          @click="scrollToSection(projectMapRef)"
        >
          <span>项目位置</span>
          <strong>威海滨海度假区</strong>
        </button>
        <button
          type="button"
          title="查看已知规模卡片"
          @click="scrollToSection(projectScaleRef)"
        >
          <span>已知规模</span>
          <strong>13 套客房，约 600㎡</strong>
        </button>
        <button
          type="button"
          title="查看建造方式卡片"
          @click="scrollToSection(buildMethodRef)"
        >
          <span>建造方式</span>
          <strong>工厂预集成 + 现场吊装</strong>
        </button>
        <button
          type="button"
          title="查看产品体系卡片"
          @click="scrollToSection(assetSectionRef)"
        >
          <span>产品体系</span>
          <strong>卡素 Capsule Cabin</strong>
        </button>
      </section>
    </section>

    <section ref="projectMapRef" class="project-map-section" id="project-map">
      <div class="section-kicker">项目位置 / 场地参考</div>
      <div class="map-frame">
        <div ref="baiduMapRef" class="baidu-map-canvas" aria-label="威海滨海度假区百度地图"></div>
        <div v-if="baiduMapStatus" class="map-status">
          <strong>{{ baiduMapStatus }}</strong>
          <span>动态地图需在 Render 构建环境中配置 VITE_BAIDU_MAP_AK。</span>
        </div>
        <a
          class="map-open-link"
          href="https://j.map.baidu.com/66/srrM"
          target="_blank"
          rel="noopener noreferrer"
        >
          打开地图
        </a>
      </div>
    </section>

    <section ref="projectScaleRef" class="scale-section" id="project-scale">
      <div class="section-kicker">已知规模 / 存量项目拆解</div>
      <div class="scale-card">
        <div class="scale-photo" aria-label="已建成胶囊客房实景">
          <div class="scale-photo-caption">
            <span>Real Unit Sample</span>
            <strong>已建成客房单元</strong>
          </div>
        </div>
        <div class="scale-copy">
          <p class="card-label">Built Case Baseline</p>
          <h2>13 套客房，约 600㎡</h2>
          <p>
            以已建成民宿作为 PoC 约束边界，把客房数量、户型组合、场地尺度与运营方式转译成 Agent 可读取的配置输入。
          </p>
          <div class="metric-grid" aria-label="项目规模指标">
            <article>
              <span>套已知客房</span>
              <strong>13</strong>
            </article>
            <article>
              <span>约计建设规模</span>
              <strong>600㎡</strong>
            </article>
            <article>
              <span>产品户型参考</span>
              <strong>38 / 56㎡</strong>
            </article>
          </div>
          <div class="scale-basis">
            <span>Agent 输入口径</span>
            <p>客房数量、面积边界、户型组合、运营方式、空间配置约束</p>
          </div>
        </div>
      </div>
    </section>

    <section ref="buildMethodRef" class="build-section" id="build-method">
      <div class="section-kicker">建造方式 / 装配式交付流程</div>
      <div class="build-card">
        <div class="build-hero">
          <div class="build-hero-copy">
            <p class="card-label">Delivery Method</p>
            <h2>工厂预集成 +<br />现场吊装</h2>
            <p>
              把结构、内装、机电与智能设备前置到工厂完成，现场聚焦运输进场、吊装定位、接驳调试与验收交付。
            </p>
          </div>
          <div class="build-hero-metrics" aria-label="建造方式关键指标">
            <article data-ghost="01">
              <strong>前置</strong>
              <span>内装 / 机电 / 智能设备</span>
            </article>
            <article data-ghost="02">
              <strong>快装</strong>
              <span>基础确认后现场吊装</span>
            </article>
            <article data-ghost="03">
              <strong>闭环</strong>
              <span>BOM、风险与验收任务可追踪</span>
            </article>
          </div>
        </div>

        <div class="build-route" aria-label="装配式交付四步流程">
          <div class="route-steps">
            <article data-ghost="01">
              <span>01</span>
              <svg class="step-icon" viewBox="0 0 120 82" aria-hidden="true">
                <path d="M12 66h96" />
                <path d="M24 66V36l22 12V36l22 12V30h20v36" />
                <path class="accent" d="M84 30V16h18v50" />
                <path class="accent" d="M38 58h18M68 58h18" />
              </svg>
              <strong>工厂预集成</strong>
              <p>机电 / 内装 / 结构同步完成</p>
            </article>
            <article data-ghost="02">
              <span>02</span>
              <svg class="step-icon" viewBox="0 0 120 82" aria-hidden="true">
                <rect x="24" y="28" width="72" height="30" rx="15" />
                <path class="accent" d="M40 28v30M82 28v30" />
                <path d="M34 66h52" />
                <path class="accent" d="M50 43h20" />
              </svg>
              <strong>出厂质检</strong>
              <p>整舱水电联测与密封验收</p>
            </article>
            <article data-ghost="03">
              <span>03</span>
              <svg class="step-icon" viewBox="0 0 120 82" aria-hidden="true">
                <path d="M22 56h66l10 10h12" />
                <path d="M32 34h48v22H32z" />
                <path class="accent" d="M42 44h24M80 44h18v12" />
                <circle cx="42" cy="68" r="7" />
                <circle cx="92" cy="68" r="7" />
              </svg>
              <strong>运输到场</strong>
              <p>模块化防护装车，低扰动进场</p>
            </article>
            <article data-ghost="04">
              <span>04</span>
              <svg class="step-icon" viewBox="0 0 120 82" aria-hidden="true">
                <path d="M24 68h68" />
                <path d="M34 68V20h44L58 32v22" />
                <path class="accent" d="M58 54c18 0 18 18 0 18s-18-18 0-18Z" />
                <path d="M34 32h14M34 44h14" />
              </svg>
              <strong>吊装接驳</strong>
              <p>基础定位、吊装、管线快接</p>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section ref="assetSectionRef" class="asset-section" id="asset-library">
      <div class="section-kicker">真实项目依据 / 产品资产库</div>
      <div class="asset-head">
        <div>
          <h2>卡素 Capsule Cabin</h2>
          <p>38㎡单体 / 56㎡拼装</p>
        </div>
      </div>

      <div class="asset-grid">
        <article class="asset-item">
          <div class="asset-visuals">
            <router-link class="asset-img-link" :to="{ path: '/project/demo-capsule-cabin', query: { source: 'asset' } }" aria-label="查看 38㎡ 单体方案详情">
              <img src="/assets/capsule_cabin/38㎡室内参考 A.png" alt="38㎡单体产品示意图" />
            </router-link>
            <figure class="plan-visual">
              <img src="/assets/capsule_cabin/38㎡ 轴测图.png?v=home-card" alt="38㎡单体轴测图" />
            </figure>
          </div>
          <div class="asset-copy">
            <p class="product-label">Capsule Cabin S</p>
            <h3>38㎡单体</h3>
            <p class="product-meta">尺寸约 10.58m × 3.20m</p>
            <ul>
              <li>空间紧凑，最多 4 人入住</li>
              <li>榻榻米、衣柜、卫浴、沙发区、水吧台、换鞋区</li>
              <li>适合自助入住与基础智能控制</li>
            </ul>
          </div>
        </article>

        <article class="asset-item">
          <div class="asset-visuals">
            <router-link class="asset-img-link" :to="{ path: '/project/demo-capsule-cabin-m', query: { source: 'asset' } }" aria-label="查看 56㎡ 拼装方案详情">
              <img src="/assets/capsule_cabin/56㎡拼装室内.png" alt="56㎡拼装产品示意图" />
            </router-link>
            <figure class="plan-visual">
              <img src="/assets/capsule_cabin/56㎡ 轴测图.png?v=home-card" alt="56㎡拼装轴测图" />
            </figure>
          </div>
          <div class="asset-copy">
            <p class="product-label">Capsule Cabin M</p>
            <h3>56㎡拼装</h3>
            <p class="product-meta">主模块约 10.58m × 3.20m，拼装扩展约 5.98m × 6.03m</p>
            <ul>
              <li>面向多人入住，空间更宽松</li>
              <li>增加活动区，可做饭，空间可灵活变换</li>
              <li>更关注隔音、隐私、空调与现场拼接质量</li>
            </ul>
          </div>
        </article>
      </div>
    </section>

    <button
      v-show="showBackTop"
      type="button"
      class="back-top-btn"
      aria-label="回到首页首屏"
      title="回到首屏"
      @click="scrollToTop"
    >
      <span aria-hidden="true">↑</span>
      <strong>置顶</strong>
    </button>
  </main>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  color: #111827;
  background: #f3f6f5;
}

.back-top-btn {
  position: fixed;
  right: 32px;
  bottom: 34px;
  z-index: 20;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 44px;
  padding: 0 16px 0 14px;
  color: #ffffff;
  font: inherit;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0;
  background: #1162ff;
  border: 0;
  border-radius: 999px;
  box-shadow: 0 14px 30px rgba(17, 98, 255, 0.28);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.back-top-btn span {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  font-size: 18px;
  line-height: 1;
  background: rgba(255, 255, 255, 0.18);
  border-radius: 999px;
}

.back-top-btn:hover {
  background: #0c55df;
  box-shadow: 0 18px 34px rgba(17, 98, 255, 0.34);
  transform: translateY(-2px);
}

.back-top-btn:focus-visible {
  outline: 3px solid rgba(17, 98, 255, 0.28);
  outline-offset: 3px;
}

.hero {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  color: #ffffff;
  background-image: url('/assets/capsule_cabin/鸟瞰图.png');
  background-position: 55% center;
  background-size: cover;
  background-repeat: no-repeat;
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(3, 14, 26, 0.94) 0%,
    rgba(3, 14, 26, 0.82) 32%,
    rgba(3, 14, 26, 0.38) 58%,
    rgba(3, 14, 26, 0.04) 86%
  );
}

.mobile-hero-image {
  display: none;
}

.hero-content {
  position: absolute;
  z-index: 1;
  top: 43%;
  left: 10vw;
  width: min(680px, 48vw);
  transform: translateY(-50%);
}

.eyebrow,
.section-kicker {
  margin: 0;
  color: #14a082;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0;
}

.hero .eyebrow {
  color: #82e6cf;
}

.hero h1 {
  margin: 18px 0 0;
  color: #ffffff;
  font-size: clamp(62px, 5.8vw, 88px);
  line-height: 1.03;
  font-weight: 860;
  letter-spacing: 0;
}

.hero h2 {
  margin: 18px 0 0;
  color: rgba(255, 255, 255, 0.96);
  font-size: clamp(32px, 3vw, 46px);
  line-height: 1.16;
  font-weight: 800;
  letter-spacing: 0;
}

.hero h3 {
  margin: 34px 0 0;
  color: #ffffff;
  font-size: 24px;
  line-height: 1.4;
  font-weight: 800;
}

.lead {
  margin: 16px 0 0;
  max-width: 640px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 17px;
  line-height: 1.85;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 30px;
}

.hero-actions :deep(.arco-btn-primary) {
  background: #1d67ff;
  border-color: #1d67ff;
}

.ghost-btn {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.13);
  border-color: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.ghost-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.48);
}

.case-strip {
  position: absolute;
  z-index: 1;
  left: 10vw;
  right: 10vw;
  bottom: 32px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  overflow: hidden;
  color: #ffffff;
  background: rgba(7, 24, 37, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  box-shadow: 0 24px 50px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(14px);
}

.case-strip div,
.case-strip button {
  min-width: 0;
  padding: 24px 28px;
  border-right: 1px solid rgba(255, 255, 255, 0.12);
}

.case-strip button {
  color: inherit;
  font: inherit;
  text-align: left;
  background: transparent;
  border-top: 0;
  border-bottom: 0;
  border-left: 0;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s ease, box-shadow 0.2s ease;
}

.case-strip button:hover {
  background: rgba(130, 230, 207, 0.12);
  box-shadow: inset 0 0 0 1px rgba(130, 230, 207, 0.35);
}

.case-strip button:hover strong {
  color: #82e6cf;
}

.case-strip div:last-child,
.case-strip button:last-child {
  border-right: 0;
}

.case-strip span {
  display: block;
  margin-bottom: 8px;
  color: #a9d9cd;
  font-size: 12px;
}

.case-strip strong {
  color: #ffffff;
  font-size: 18px;
  line-height: 1.35;
}

.project-map-section,
.scale-section,
.build-section,
.asset-section {
  width: calc(100% - 12vw);
  margin: 0 auto;
}

.project-map-section,
.scale-section,
.build-section,
.asset-section {
  scroll-margin-top: 24px;
}

.project-map-section {
  padding: 84px 0 96px;
}

.map-frame {
  position: relative;
  height: min(620px, 58vw);
  min-height: 420px;
  margin-top: 16px;
  overflow: hidden;
  background: #e4ebef;
  border: 1px solid #dbe4e8;
  border-radius: 8px;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.12);
}

.baidu-map-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.map-status {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  color: #334155;
  text-align: center;
  background: linear-gradient(135deg, #e2edf2, #f8fbfc);
}

.map-status strong {
  color: #083344;
  font-size: 16px;
}

.map-status span {
  max-width: 520px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.map-open-link {
  position: absolute;
  right: 18px;
  top: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 0 14px;
  color: #083344;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(15, 118, 110, 0.22);
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(8px);
}

.map-open-link:hover {
  color: #0f766e;
  border-color: rgba(15, 118, 110, 0.45);
}

.scale-section {
  padding: 96px 0;
}

.scale-card {
  display: grid;
  grid-template-columns: minmax(320px, 0.78fr) minmax(0, 1.22fr);
  gap: 0;
  align-items: stretch;
  margin-top: 16px;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #dfe8e6;
  border-radius: 8px;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.scale-photo {
  position: relative;
  min-height: 420px;
  background-image:
    linear-gradient(180deg, rgba(4, 17, 30, 0.05), rgba(4, 17, 30, 0.62)),
    url('/assets/capsule_cabin/正面图.JPG');
  background-position: center;
  background-size: cover;
}

.scale-photo::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 68%, rgba(255, 255, 255, 0.18));
}

.scale-photo-caption {
  position: absolute;
  z-index: 1;
  left: 24px;
  right: 24px;
  bottom: 24px;
  padding: 16px 18px;
  color: #ffffff;
  background: rgba(5, 22, 35, 0.56);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  backdrop-filter: blur(14px);
}

.scale-photo-caption span {
  display: block;
  color: #82e6cf;
  font-size: 12px;
  font-weight: 900;
}

.scale-photo-caption strong {
  display: block;
  margin-top: 6px;
  font-size: 20px;
  line-height: 1.3;
}

.card-label {
  margin: 0 0 10px;
  color: #0b735f;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0;
}

.scale-copy {
  min-width: 0;
  padding: 42px 46px;
  background:
    radial-gradient(circle at 92% 12%, rgba(255, 139, 183, 0.16), transparent 25%),
    linear-gradient(135deg, #ffffff 0%, #f7fbfa 100%);
}

.scale-copy h2,
.build-hero-copy h2 {
  margin: 0;
  color: #111827;
  font-size: 38px;
  line-height: 1.22;
  letter-spacing: 0;
}

.scale-copy p,
.build-hero-copy p {
  margin: 14px 0 0;
  color: #536170;
  font-size: 16px;
  line-height: 1.85;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 28px;
}

.metric-grid article {
  min-width: 0;
  min-height: 148px;
  padding: 20px;
  background: #ffffff;
  border: 1px solid #e3e8eb;
  border-radius: 8px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.metric-grid strong {
  display: block;
  margin-top: 18px;
  color: #0b1f2a;
  font-size: 36px;
  line-height: 1.1;
  white-space: nowrap;
}

.metric-grid span {
  display: block;
  color: #536170;
  font-size: 13px;
  font-weight: 700;
}

.scale-basis {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 16px;
  align-items: center;
  margin-top: 18px;
  padding: 16px 18px;
  background: rgba(11, 115, 95, 0.06);
  border: 1px solid rgba(11, 115, 95, 0.14);
  border-radius: 8px;
}

.scale-basis span {
  color: #0b735f;
  font-size: 13px;
  font-weight: 900;
  white-space: nowrap;
}

.scale-basis p {
  margin: 0;
  color: #536170;
  font-size: 14px;
  line-height: 1.65;
}

.build-section {
  padding: 96px 0;
}

.build-card {
  margin-top: 16px;
  overflow: hidden;
  background: #071725;
  border: 1px solid rgba(7, 24, 37, 0.16);
  border-radius: 8px;
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.18);
}

.build-hero {
  position: relative;
  min-height: 610px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  align-items: start;
  gap: 32px;
  padding: 72px 68px;
  color: #ffffff;
  background-image:
    linear-gradient(90deg, rgba(4, 17, 30, 0.96) 0%, rgba(4, 17, 30, 0.74) 42%, rgba(4, 17, 30, 0.18) 100%),
    linear-gradient(0deg, rgba(4, 17, 30, 0.9), rgba(4, 17, 30, 0.08) 48%),
    url('/assets/capsule_cabin/人视图.png');
  background-position: center;
  background-size: cover;
}

.build-hero::after {
  content: "";
  position: absolute;
  inset: auto 42px 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(130, 230, 207, 0.58), transparent);
}

.build-hero-copy,
.build-hero-metrics {
  position: relative;
  z-index: 1;
}

.build-hero-copy {
  align-self: center;
  max-width: 620px;
}

.build-hero-copy .card-label {
  color: #82e6cf;
}

.build-hero-copy h2 {
  color: #ffffff;
  font-size: clamp(58px, 5.7vw, 82px);
  line-height: 0.98;
}

.build-hero-copy p {
  max-width: 560px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 17px;
  line-height: 1.85;
}

.build-hero-metrics {
  justify-self: end;
  display: flex;
  gap: 0;
  padding: 6px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 28px;
  backdrop-filter: blur(18px);
}

.build-hero-metrics article {
  padding: 10px 18px;
  background: rgba(8, 22, 34, 0.32);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 22px;
}

.build-hero-metrics strong {
  display: block;
  color: #ffffff;
  font-size: 15px;
}

.build-hero-metrics span {
  display: none;
}

.build-route {
  padding: 30px 48px 48px;
  background:
    radial-gradient(circle at 78% 0%, rgba(255, 126, 174, 0.16), transparent 28%),
    linear-gradient(180deg, #071725 0%, #0b2231 100%);
}

.route-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
}

.route-head .card-label {
  margin-bottom: 8px;
  color: #82e6cf;
}

.route-head h3 {
  margin: 0;
  color: #ffffff;
  font-size: 24px;
  line-height: 1.35;
}

.route-head::after {
  content: "PoC Flow";
  flex: 0 0 auto;
  color: rgba(255, 255, 255, 0.14);
  font-size: 40px;
  font-weight: 900;
}

.process-visual {
  min-width: 0;
  overflow: hidden;
  padding: 8px 12px 0;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.02)),
    rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.process-visual svg {
  display: block;
  width: 100%;
  height: auto;
}

.route-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.route-steps article {
  position: relative;
  min-width: 0;
  min-height: 278px;
  padding: 24px 24px 22px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
}

.route-steps article::before {
  content: attr(data-ghost);
  position: absolute;
  top: 18px;
  right: 18px;
  color: rgba(255, 255, 255, 0.04);
  font-size: 48px;
  font-weight: 900;
  line-height: 1;
}

.route-steps article::after {
  content: "";
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 28px;
  height: 1px;
  background: linear-gradient(90deg, #ff8db6, #6fe3cf, transparent);
  opacity: 0.72;
}

.route-steps span {
  position: relative;
  z-index: 1;
  display: block;
  color: #82e6cf;
  font-size: 13px;
  font-weight: 900;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.route-steps strong {
  position: relative;
  z-index: 1;
  display: block;
  margin-top: 18px;
  color: #ffffff;
  font-size: 25px;
  line-height: 1.2;
}

.route-steps p {
  position: relative;
  z-index: 1;
  min-height: 44px;
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.66);
  font-size: 14px;
  line-height: 1.65;
}

.step-icon {
  position: relative;
  z-index: 1;
  display: block;
  width: 118px;
  height: 82px;
  margin: 34px auto 12px;
}

.step-icon path,
.step-icon rect,
.step-icon circle {
  fill: none;
  stroke: rgba(255, 255, 255, 0.74);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.step-icon .accent {
  stroke: #ff9abb;
}

.asset-head h2 {
  margin: 0;
  font-size: 38px;
  line-height: 1.22;
  letter-spacing: 0;
}

.asset-head p {
  margin: 0;
  color: #536170;
  font-size: 16px;
  line-height: 1.9;
}

.asset-section {
  padding: 96px 0;
}

.asset-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 24px;
  margin-top: 12px;
}

.asset-head p {
  margin-top: 8px;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 34px;
  margin-top: 38px;
}

.asset-item {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 52%) minmax(320px, 48%);
  grid-template-rows: 306px 286px;
  min-height: 0;
  background:
    linear-gradient(180deg, #ffffff 0%, #fbfdfc 48%, #f7fbfa 100%);
  border: 1px solid #dfe7eb;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 24px 54px rgba(15, 23, 42, 0.1);
}

.asset-visuals {
  display: contents;
}

.asset-img-link {
  position: relative;
  display: block;
  grid-column: 1;
  grid-row: 1;
  width: auto;
  height: auto;
  overflow: hidden;
  border-top-left-radius: 8px;
  border-bottom: 1px solid #e6edf0;
  border-right: 1px solid #e6edf0;
}

.asset-img-link img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #f8faf9;
  display: block;
  transition: transform 0.3s ease, filter 0.3s ease;
}

.asset-img-link::after {
  content: "查看方案 →";
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 14px 18px;
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  background: linear-gradient(0deg, rgba(3, 14, 26, 0.55) 0%, transparent 50%);
  opacity: 0;
  transition: opacity 0.25s ease;
  pointer-events: none;
}

.asset-img-link:hover img {
  transform: scale(1.04);
  filter: brightness(0.92);
}

.asset-img-link:hover::after {
  opacity: 1;
}

.asset-img-link:focus-visible {
  outline: 2px solid #1d67ff;
  outline-offset: -2px;
}

.asset-copy {
  position: relative;
  z-index: 2;
  grid-column: 2;
  grid-row: 1;
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: auto;
  margin: 0;
  padding: 34px 34px 32px;
  background: #ffffff;
  border-bottom: 1px solid #e6edf0;
  border-radius: 0;
  box-shadow: none;
  backdrop-filter: none;
}

.plan-visual {
  position: relative;
  z-index: 1;
  grid-column: 1 / -1;
  grid-row: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
  margin: 24px 24px 24px;
  background: #ffffff;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 2px;
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.13);
}

.plan-visual img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
  padding: 10px 14px;
}

.asset-item:nth-child(2) .plan-visual {
  margin: 24px 24px 24px;
}

.asset-item:nth-child(2) .asset-copy {
  margin-right: 0;
}

.product-label {
  margin: 0 0 12px;
  color: #0b735f;
  font-size: 14px;
  font-weight: 900;
}

.asset-copy h3 {
  margin: 0;
  color: #0d1b2a;
  font-size: 31px;
  line-height: 1.12;
  letter-spacing: 0;
}

.product-meta {
  margin: 14px 0 14px;
  color: #536170;
  font-size: 15px;
  line-height: 1.65;
}

.asset-copy ul {
  margin: 0;
  padding-left: 18px;
  color: #536170;
  font-size: 15px;
  line-height: 1.72;
}

.asset-copy li + li {
  margin-top: 3px;
}

@media (max-width: 1080px) {
  .hero-content {
    width: min(720px, 62vw);
  }

  .case-strip {
    grid-template-columns: repeat(2, 1fr);
  }

  .scale-card,
  .build-hero {
    grid-template-columns: 1fr;
  }

  .scale-photo {
    min-height: 360px;
  }

  .build-hero-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .route-steps {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .asset-grid {
    grid-template-columns: 1fr;
  }

  .asset-item {
    grid-template-columns: minmax(0, 56%) minmax(300px, 44%);
  }

  .plan-visual {
    grid-column: 1 / -1;
    grid-row: 2;
  }
}

@media (max-width: 720px) {
  .back-top-btn {
    right: 18px;
    bottom: 18px;
    height: 40px;
    padding: 0 13px 0 11px;
    font-size: 13px;
  }

  .back-top-btn span {
    width: 20px;
    height: 20px;
    font-size: 16px;
  }

  .hero {
    display: block;
    min-height: 0;
    background: #071725;
  }

  .hero::before {
    display: none;
  }

  .mobile-hero-image {
    display: block;
    height: 46vh;
    min-height: 320px;
    background-image: url('/assets/capsule_cabin/鸟瞰图.png');
    background-position: 55% center;
    background-size: cover;
    background-repeat: no-repeat;
  }

  .hero-content {
    position: static;
    width: auto;
    max-width: none;
    padding: 34px 24px 42px;
    transform: none;
    background: #071725;
  }

  .hero h1 {
    font-size: 42px;
  }

  .hero h2 {
    font-size: 25px;
  }

  .hero h3 {
    margin-top: 30px;
    font-size: 21px;
  }

  .lead {
    font-size: 16px;
  }

  .case-strip {
    position: static;
    grid-template-columns: 1fr;
    margin: 0;
    background: #071725;
    border: 0;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 0;
    box-shadow: none;
  }

  .case-strip button {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 16px;
    padding: 20px 24px;
    border-right: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  }

  .case-strip button:last-child {
    border-bottom: 0;
  }

  .case-strip span {
    margin-bottom: 0;
    white-space: nowrap;
  }

  .case-strip strong {
    font-size: 17px;
    text-align: right;
  }

  .project-map-section,
  .scale-section,
  .build-section,
  .asset-section {
    width: calc(100% - 36px);
  }

  .project-map-section,
  .scale-section,
  .build-section {
    padding-top: 46px;
  }

  .map-frame {
    height: 440px;
    min-height: 440px;
  }

  .scale-copy,
  .build-hero,
  .build-route {
    padding: 22px;
  }

  .scale-copy h2,
  .build-hero-copy h2,
  .asset-head h2 {
    font-size: 28px;
  }

  .metric-grid,
  .build-hero-metrics,
  .route-steps {
    grid-template-columns: 1fr;
  }

  .scale-photo {
    min-height: 320px;
  }

  .scale-basis {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .route-head {
    display: block;
  }

  .route-head::after {
    display: none;
  }

  .process-visual {
    overflow-x: auto;
  }

  .process-visual svg {
    min-width: 680px;
  }

  .build-hero {
    min-height: 520px;
    align-items: end;
    background-position: 58% center;
  }

  .asset-grid {
    grid-template-columns: 1fr;
  }

  .asset-head {
    display: block;
  }

  .asset-item {
    display: block;
    min-height: auto;
    overflow: hidden;
  }

  .asset-visuals {
    position: static;
  }

  .asset-img-link {
    width: 100%;
    height: 230px;
    border-top-right-radius: 8px;
  }

  .asset-img-link::after {
    padding: 12px 14px;
    font-size: 12px;
  }

  .asset-copy {
    position: static;
    width: auto;
    margin: 0;
    border-radius: 0;
    box-shadow: none;
    border-width: 0 0 1px;
  }

  .plan-visual {
    position: static;
    height: 310px;
    margin: 0;
    box-shadow: none;
    border-width: 0;
  }

  .asset-item:nth-child(2) .plan-visual,
  .asset-item:nth-child(2) .asset-copy {
    left: auto;
    right: auto;
  }
}
</style>
