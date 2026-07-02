<template>
  <main class="project-detail-page">
    <header class="page-header">
      <a-button class="ghost-action" @click="$router.back()">返回</a-button>
      <div>
        <p class="eyebrow">PoC 方案成果 / 动态推荐页</p>
        <h1>{{ activeProfile.headline }}</h1>
        <p>主线展示当前推荐方案，同时保留 38㎡ / 56㎡ 的决策对比，避免变成割裂的产品目录。</p>
      </div>
      <a-button type="primary" @click="$router.push('/chat')">进入 Agent 规划台</a-button>
    </header>

    <a-spin :loading="loading">
      <template v-if="project">
        <section class="hero-board">
          <article class="decision-copy">
            <p class="recommendation-kicker">Recommendation</p>
            <h2>{{ activeProfile.name }}</h2>
            <div class="evaluation-panel">
              <div class="match-score">
                <svg viewBox="0 0 120 120" aria-hidden="true">
                  <circle cx="60" cy="60" r="48" />
                  <circle cx="60" cy="60" r="48" />
                </svg>
                <span class="score-pill">Recommended</span>
                <svg class="score-icon" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M6.5 15.4C7.4 11.6 10.1 9.5 12 9.5s4.6 2.1 5.5 5.9" />
                  <path d="M12 12.5l2.6-2.6" />
                </svg>
                <strong>{{ activeProfile.key === 's' ? '94%' : '89%' }}</strong>
                <small>AI Match Score</small>
              </div>
              <div class="evaluation-content">
                <div class="evaluation-head">
                  <span><IconRobot /></span>
                  <div>
                    <p>Agent Evaluation</p>
                    <h3>推荐命中依据</h3>
                  </div>
                </div>
                <div class="evaluation-grid">
                  <section>
                    <svg class="sparkle-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M12 2.8l1.7 5.1 5.1 1.7-5.1 1.7-1.7 5.1-1.7-5.1-5.1-1.7 5.1-1.7L12 2.8Z" />
                      <path d="M18.3 13.8l.8 2.4 2.4.8-2.4.8-.8 2.4-.8-2.4-2.4-.8 2.4-.8.8-2.4Z" />
                    </svg>
                    <b>{{ activeProfile.key === 's' ? 'Best fit' : 'Family fit' }}</b><p>{{ activeProfile.key === 's' ? '单体扩建' : '多人入住' }}</p>
                  </section>
                  <section><IconCheckCircle /><b>{{ activeProfile.key === 's' ? 'Low' : 'Medium' }}</b><p>交付风险</p></section>
                  <section><IconUserGroup /><b>{{ activeProfile.key === 's' ? '4 guests' : '6 guests' }}</b><p>入住容量</p></section>
                  <section>
                    <svg class="key-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <circle cx="8" cy="12" r="3.4" />
                      <path d="M11.4 12H21M17.2 12v3M14.8 12v2" />
                    </svg>
                    <b>Ready</b><p>自助运营</p>
                  </section>
                </div>
                <p class="evaluation-note"><IconThunderbolt />面积、客群与低复杂度交付条件同时满足，适合作为主线推荐方案。</p>
              </div>
            </div>
          </article>

          <article class="hero-visual">
            <img :src="activeProfile.images.interior" :alt="`${activeProfile.name}室内参考`" />
          </article>
        </section>

        <section class="section-card comparison-section">
          <div class="section-head">
            <div>
              <p class="eyebrow">Decision Logic</p>
              <h2>38㎡ / 56㎡ 决策对比</h2>
            </div>
            <p>这里展示 Agent 为什么选择当前方案，而不是把两个户型拆成互不相干的详情页。</p>
          </div>

          <div class="compare-grid">
            <article
              v-for="profile in profiles"
              :key="profile.key"
              :class="['compare-card', { active: profile.key === activeProfile.key }]"
            >
              <div class="compare-media">
                <img :src="profile.images.axon" :alt="`${profile.shortName}轴测图`" />
              </div>
              <div class="compare-body">
                <p class="product-label">{{ profile.product }}</p>
                <h3>{{ profile.shortName }}</h3>
                <p>{{ profile.fit }}</p>
                <ul>
                  <li v-for="item in profile.decisionPoints" :key="item">{{ item }}</li>
                </ul>
              </div>
            </article>
          </div>
        </section>

        <section class="section-card smart-device-map">
          <div class="device-map-header">
            <div>
              <h2>{{ activeSmartDeviceMap.title }}</h2>
              <p>{{ activeSmartDeviceMap.subtitle }}</p>
            </div>
            <a-button type="primary" :href="activeSmartDeviceMap.figmaUrl" target="_blank">打开 Figma 编辑</a-button>
          </div>

          <div class="figma-embed-frame">
            <iframe
              :src="activeSmartDeviceMap.embedUrl"
              allowfullscreen
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
            />
          </div>
          <p class="figma-embed-note">如需直接拖动点位或调整底图，请点击右上角“打开 Figma 编辑”。网页内嵌视图是否可编辑取决于 Figma 登录状态与文件权限。</p>
        </section>

        <section class="section-card configuration-section">
          <div class="configuration-hero">
            <div>
              <p class="configuration-kicker"><span></span>Configuration Output</p>
              <h2>配置成果</h2>
              <p>围绕 {{ activeProfile.area }}㎡滨海住宿单元，沉淀空间、家具、机电与智能化的可执行清单。</p>
            </div>
            <span class="generated-badge"><IconThunderbolt />智能空间方案已生成</span>
          </div>

          <div class="config-grid">
            <article class="config-card compact-card">
              <div class="config-card-title">
                <span><IconHome /></span>
                <h3>空间模块</h3>
              </div>
              <div class="module-chip-list">
                <span v-for="item in config.space_modules" :key="item" class="module-chip">
                  <component :is="resolveConfigIcon(item)" />
                  {{ item }}
                </span>
              </div>
            </article>
            <article class="config-card compact-card">
              <div class="config-card-title">
                <span><IconThunderbolt /></span>
                <h3>智能设备</h3>
              </div>
              <div class="smart-chip-list">
                <span v-for="item in config.smart_devices" :key="item" class="smart-chip">
                  <component :is="resolveConfigIcon(item)" />
                  {{ item }}
                </span>
              </div>
            </article>
            <article class="config-card list-card">
              <div class="config-card-title">
                <span><IconCheckCircle /></span>
                <h3>配置清单</h3>
              </div>
              <div class="configuration-items-grid">
                <div v-for="item in displayConfigurationItems" :key="item" class="configuration-item">
                  <span><component :is="resolveConfigIcon(item)" /></span>
                  <p>{{ item }}</p>
                </div>
              </div>
            </article>
            <article class="config-card basis-card">
              <div class="config-card-title">
                <span><IconSafe /></span>
                <h3>推荐依据</h3>
              </div>
              <div class="basis-list">
                <div v-for="(item, index) in config.recommendation_basis" :key="item" class="basis-item">
                  <span>{{ index + 1 }}</span>
                  <p>{{ item }}</p>
                </div>
              </div>
            </article>
          </div>
        </section>

        <section class="section-card agent-value">
          <div class="section-head">
            <div>
              <p class="eyebrow">AI Product Value</p>
              <h2>Agent 在方案页沉淀的能力</h2>
            </div>
          </div>
          <div class="value-grid">
            <article v-for="item in aiValueItems" :key="item.title">
              <span>{{ item.index }}</span>
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </article>
          </div>
        </section>

        <section class="section-card delivery-section">
          <div class="section-head">
            <div>
              <p class="eyebrow">Delivery Board</p>
              <h2>交付阶段、任务与验收点</h2>
            </div>
            <p>面向项目经理的交付看板：每个阶段保留任务、验收与人工确认口径。</p>
          </div>

          <div class="delivery-board">
            <article v-for="(phase, index) in delivery.delivery_phases" :key="phase.phase" class="phase-card">
              <span>{{ String(index + 1).padStart(2, '0') }}</span>
              <h3>{{ phase.phase }}</h3>
              <p><strong>任务</strong>{{ phase.tasks.join('、') }}</p>
              <p><strong>验收</strong>{{ phase.acceptance_criteria.join('、') }}</p>
              <p><strong>风险</strong>{{ phase.risks.join('、') }}</p>
            </article>
          </div>
        </section>

        <section class="section-card boundary-section">
          <article>
            <p class="eyebrow">Risk & Boundary</p>
            <h2>风险与 PoC 边界</h2>
            <ul>
              <li v-for="risk in delivery.site_risks" :key="risk">{{ risk }}</li>
            </ul>
          </article>
          <article class="source-note">
            <h3>真实项目依据</h3>
            <p>{{ config.data_source_note || project.data_source_note }}</p>
            <p>{{ project.disclaimer }}</p>
            <strong>{{ config.budget_range?.note }}</strong>
          </article>
        </section>
      </template>
    </a-spin>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { agentApi } from '../api/agent'
import {
  IconApps,
  IconBulb,
  IconCheckCircle,
  IconDashboard,
  IconHome,
  IconRobot,
  IconSafe,
  IconStorage,
  IconThunderbolt,
  IconTool,
  IconUserGroup,
  IconWifi,
} from '@arco-design/web-vue/es/icon'

const route = useRoute()
const project = ref<any>(null)
const loading = ref(false)
const config = computed(() => project.value?.configuration || {})
const delivery = computed(() => project.value?.delivery || {})
const displayConfigurationItems = computed(() => (config.value?.configuration_items || []).slice(0, 10))

const resolveConfigIcon = (item: string) => {
  const text = item || ''
  if (text.includes('门锁') || text.includes('客控') || text.includes('智能')) return IconRobot
  if (text.includes('灯光') || text.includes('电源') || text.includes('220V')) return IconBulb
  if (text.includes('Wi-Fi') || text.includes('网络') || text.includes('电视')) return IconWifi
  if (text.includes('卫浴') || text.includes('热水') || text.includes('水吧') || text.includes('排水')) return IconThunderbolt
  if (text.includes('床') || text.includes('沙发') || text.includes('座椅') || text.includes('茶几')) return IconStorage
  if (text.includes('监控') || text.includes('传感') || text.includes('烟雾') || text.includes('消防')) return IconSafe
  if (text.includes('衣柜') || text.includes('挂衣') || text.includes('收纳') || text.includes('行李')) return IconApps
  return IconHome
}
const toFigmaEmbedUrl = (url: string) => `https://www.figma.com/embed?embed_host=share&url=${encodeURIComponent(url)}`
const smartDevice38Url = 'https://www.figma.com/design/WTP8BirpfGTJychHs4KC7c/38%E3%8E%A1%E6%88%B7%E5%9E%8B%EF%BD%9C%E6%99%BA%E8%83%BD%E8%AE%BE%E5%A4%87%E7%82%B9%E4%BD%8D%E5%9B%BE?node-id=0-1&t=bsMX6jAMny8H4XT5-1'
const smartDevice56Url = 'https://www.figma.com/design/fii9Ywvy3zFe6hbHae0aoT/56%E3%8E%A1%E6%88%B7%E5%9E%8B%EF%BD%9C%E6%99%BA%E8%83%BD%E8%AE%BE%E5%A4%87%E7%82%B9%E4%BD%8D%E5%9B%BE?node-id=0-1&t=Ccn5RsQAkzUr0ad5-1'
const smartDevice38EmbedUrl = 'https://www.figma.com/file/WTP8BirpfGTJychHs4KC7c/38sqm-smart-device-placement?node-id=0%3A1&t=bsMX6jAMny8H4XT5-1'
const smartDevice56EmbedUrl = 'https://www.figma.com/file/fii9Ywvy3zFe6hbHae0aoT/56sqm-smart-device-placement?node-id=0%3A1&t=Ccn5RsQAkzUr0ad5-1'
const smartDeviceMaps = {
  s: {
    title: '38㎡ 智能设备点位图',
    subtitle: 'Figma Embedded Board · 登录后可在 Figma 中直接编辑',
    figmaUrl: smartDevice38Url,
    embedUrl: toFigmaEmbedUrl(smartDevice38EmbedUrl)
  },
  m: {
    title: '56㎡ 智能设备点位图',
    subtitle: 'Figma Embedded Board · 登录后可在 Figma 中直接编辑',
    figmaUrl: smartDevice56Url,
    embedUrl: toFigmaEmbedUrl(smartDevice56EmbedUrl)
  }
}

const profiles = [
  {
    key: 's',
    area: 38,
    product: 'Capsule Cabin S',
    shortName: '38㎡单体',
    name: 'Capsule Cabin S / 38㎡ 单体',
    headline: '推荐方案：38㎡ 单体配置',
    guests: '1-4 人 / 标准客房 / 自助入住',
    complexity: '低',
    fit: '适合标准单体扩建、轻量运营和基础智能控制，是 PoC 默认演示方案。',
    reason: '输入以单体扩建、面积控制或标准房型为主，优先匹配 38㎡单体产品。',
    decisionPoints: ['空间紧凑，最多 4 人入住', '交付链路更轻，适合快速复制', '不适合多人活动区、做饭或更强空间弹性需求'],
    images: {
      interior: '/assets/capsule_cabin/38㎡室内参考 A.png',
      alternateInterior: '/assets/capsule_cabin/38㎡室内参考 B.jpg',
      plan: '/assets/capsule_cabin/38㎡ 户型图.png',
      axon: '/assets/capsule_cabin/38㎡ 轴测图.png'
    }
  },
  {
    key: 'm',
    area: 56,
    product: 'Capsule Cabin M',
    shortName: '56㎡拼装',
    name: 'Capsule Cabin M / 56㎡ 拼装',
    headline: '推荐方案：56㎡ 拼装配置',
    guests: '多人 / 亲子 / 小团体',
    complexity: '中',
    fit: '适合多人入住、活动区、简餐和空间灵活变换，但交付确认项更多。',
    reason: '输入包含多人、亲子、活动区、做饭或空间宽松需求时，优先匹配 56㎡拼装产品。',
    decisionPoints: ['空间更宽松，功能弹性更强', '更适合多人和亲子场景', '需要重点确认拼接、隔音、空调与现场安装质量'],
    images: {
      interior: '/assets/capsule_cabin/56㎡拼装室内.png',
      plan: '/assets/capsule_cabin/56㎡ 户型图.png',
      axon: '/assets/capsule_cabin/56㎡ 轴测图.png'
    }
  }
]

const activeProfile = computed(() => {
  const area = Number(config.value?.recommended_area_sqm || 38)
  return area >= 56 ? profiles[1] : profiles[0]
})
const activeSmartDeviceMap = computed(() => smartDeviceMaps[activeProfile.value.key as keyof typeof smartDeviceMaps])

const aiValueItems = computed(() => {
  const opportunities = delivery.value?.ai_opportunities || config.value?.ai_opportunities || []
  const fallback = ['需求解析', '产品匹配', '配置清单生成', '交付阶段拆解', '风险与验收提示']
  return (opportunities.length ? opportunities : fallback).slice(0, 5).map((title: string, index: number) => ({
    index: String(index + 1).padStart(2, '0'),
    title,
    desc: ['把业主输入转成结构化需求', '在 38㎡ / 56㎡ 中形成推荐判断', '沉淀为空间、家具、机电与智能设备清单', '拆成可执行的项目阶段', '把风险点留给人工确认'][index] || '保留人工确认边界'
  }))
})

const createConfig = (profile: typeof profiles[number]) => ({
  recommended_product: profile.product,
  recommended_area_sqm: profile.area,
  target_guests: profile.guests,
  operation_mode: '偏无人化运营，自助入住 + 基础智能控制',
  intelligence_level: '基础',
  recommendation_reason: profile.reason,
  recommendation_basis: profile.key === 'm'
    ? ['56㎡拼装产品解决多人入住、活动区、做饭和空间灵活变换问题。', '偏无人化运营关注入住效率、维护成本、拍照传播和舒适度。', '自助入住场景需要智能门锁、灯光、空调、窗帘、传感器、监控与稳定网络。', '滨海场地需要提前关注防腐、防水、潮湿、风、排水、供电网络和吊装条件。']
    : ['38㎡单体产品空间紧凑，不严格限定客群，最多 4 人入住。', '偏无人化运营关注入住效率、维护成本、拍照传播和舒适度。', '自助入住场景需要智能门锁、灯光、空调、窗帘、传感器、监控与稳定网络。', '滨海场地需要提前关注防腐、防水、潮湿、风、排水、供电网络和吊装条件。'],
  data_source_note: '基于瑞泽·海度假民宿已建项目参与经验、产品资料图、户型图与现场交付复盘整理；非合同、报价或正式工程记录。',
  space_modules: profile.key === 'm'
    ? ['睡眠区', '卫浴', '活动区', '简餐/烹饪区', '水吧台', '收纳区', '灵活变换区']
    : ['榻榻米', '衣柜/挂衣空间', '卫浴', '沙发区', '水吧台', '换鞋区'],
  configuration_items: profile.key === 'm'
    ? ['1.8m 双人床与床头阅读灯', '整体卫浴模块', '双人休闲座椅与小圆桌', '迷你茶吧、冰箱位与开放收纳', '入口换鞋与行李暂存区', '粉白色系软装、耐潮墙面与易清洁地面', '空调/供暖设备', '220V电源插座', '烟雾报警器等消防设施', '稳定 Wi-Fi、电视']
    : ['床和品质较好的床垫', '床头柜、写字台、座椅、茶几', '衣橱/挂衣空间、衣架、行李架', '干湿分离卫浴', '24小时冷水/定时热水', '电热水壶、茶包/咖啡、瓶装水', '空调/供暖设备', '220V电源插座', '烟雾报警器等消防设施', '稳定 Wi-Fi、电视'],
  smart_devices: ['智能门锁', '灯光控制', '空调控制', '窗帘控制', '传感器', '监控', '稳定 Wi-Fi'],
  ai_opportunities: ['业主方需求问卷生成', '面积和 BOM 表控制', '生产端进度管理', '现场交付风险检查', '验收任务拆解'],
  budget_range: { level: '中档', note: '示例配置预算区间，仅用于规则型 PoC 演示，不构成正式报价。' }
})

const createDelivery = () => ({
  site_risks: ['滨海环境风险：防腐、防水、潮湿、风。', '现场交付条件：吊装空间、道路运输、基础不平、排水、防水、防腐、供电网络需提前确认。', '现场施工最大风险之一是材料到货，需联动 BOM 与生产进度。', '室内体验易忽略隔音、隐私和空调，需要进入验收清单。', '消防、结构、安全和审批要求不由 PoC 自动确认。'],
  high_risk_phases: ['工厂加工/预制', '拼接安装', '调试验收'],
  ai_opportunities: ['业主方需求问卷生成', '面积和 BOM 表控制', '生产端进度管理', '现场交付风险检查', '验收任务拆解'],
  delivery_phases: [
    { phase: '设计确认', tasks: ['生成业主方需求问卷', '确认产品型号、面积和入住人数边界', '确认标配/选配和智能化等级'], acceptance_criteria: ['形成已确认配置表', '关键需求进入面积与 BOM 控制清单'], risks: ['需求端信息不完整会影响后续设计、BOM 和生产排期'] },
    { phase: '工厂加工/预制', tasks: ['按确认方案进入工厂加工', '核对模块尺寸、材料、家具和智能设备预留', '跟踪材料到货与生产进度'], acceptance_criteria: ['BOM 与配置表一致', '关键预留点位完成出厂检查'], risks: ['材料到货、尺寸偏差和预留点位会影响现场安装'] },
    { phase: '运输', tasks: ['核对运输尺寸', '确认道路条件与到场时间', '确认包装保护和临停空间'], acceptance_criteria: ['运输尺寸、道路条件和到场窗口经人工确认'], risks: ['道路运输、限高、转弯半径和现场临停条件可能影响到场'] },
    { phase: '现场基础', tasks: ['检查基础平整度', '确认排水、防水、防腐条件', '确认供电网络预留'], acceptance_criteria: ['基础、排水、防水、防腐、供电网络达到安装前置条件'], risks: ['基础不平、排水、防水、防腐和供电网络是关键问题'] },
    { phase: '吊装', tasks: ['确认吊装空间', '按单体逐套推进吊装', '确认风力和现场安全条件'], acceptance_criteria: ['吊装作业面、吊装顺序和现场安全条件经人工确认'], risks: ['滨海场地需关注风、吊装空间和现场安全'] },
    { phase: '拼接安装', tasks: ['完成模块拼接', '检查连接、密封、防水节点', '核对隔音、隐私和空调体验'], acceptance_criteria: ['拼接节点、密封、防水和室内体验问题完成检查'], risks: ['拼接精度、防水、隔音、隐私和空调容易被忽略'] },
    { phase: '调试验收', tasks: ['调试智能门锁、灯光、空调、窗帘、传感器、监控和网络', '核对配置清单', '整理验收问题清单'], acceptance_criteria: ['智能设备可用', '网络和供电稳定', '形成验收记录'], risks: ['设备调试、网络和供电稳定性会影响无人化运营体验'] }
  ]
})

const createLocalProject = (profile: typeof profiles[number]) => ({
  title: `瑞泽·海度假民宿 ${profile.shortName}配置（规则型 PoC）`,
  data_source_note: '基于瑞泽·海度假民宿已建项目参与经验、产品资料图、户型图与现场交付复盘整理；非合同、报价或正式工程记录。',
  disclaimer: '本案例为基于瑞泽·海度假民宿已建项目经验复盘的规则型 AI PoC；配置、预算与周期均为示例，不构成正式设计、报价或施工承诺。',
  configuration: createConfig(profile),
  delivery: createDelivery()
})

const localProjects: Record<string, any> = {
  'demo-capsule-cabin': createLocalProject(profiles[0]),
  'demo-capsule-cabin-m': createLocalProject(profiles[1])
}

const loadProject = async () => {
  const id = route.params.id as string
  loading.value = true
  try {
    const fromStaticEntry = route.query.source === 'asset' || route.query.source === 'home-poc'
    const snapshot = window.localStorage.getItem('capsule_cabin_current_project')
    if (snapshot && !fromStaticEntry && id === 'demo-capsule-cabin') {
      project.value = JSON.parse(snapshot)
    } else if (localProjects[id]) {
      project.value = localProjects[id]
    } else {
      project.value = await agentApi.getDemoProject() as any
    }
  } catch {
    project.value = localProjects[id] || localProjects['demo-capsule-cabin']
  } finally {
    loading.value = false
  }
}

onMounted(loadProject)
watch(() => [route.params.id, route.query.source], loadProject)
</script>

<style scoped>
.project-detail-page {
  min-height: 100vh;
  padding: 24px;
  color: #111827;
  background:
    radial-gradient(circle at 4% 0%, rgba(20, 160, 130, 0.14), transparent 26%),
    radial-gradient(circle at 92% 0%, rgba(244, 130, 166, 0.13), transparent 28%),
    #f4f7f6;
}

.page-header,
.hero-board,
.section-card {
  width: min(1180px, 100%);
  margin-inline: auto;
}

.page-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}

.page-header h1 {
  margin: 0;
  color: #0d1b2a;
  font-size: 30px;
  line-height: 1.2;
}

.page-header p:last-child {
  margin: 8px 0 0;
  color: #607188;
}

.eyebrow {
  margin: 0 0 8px;
  color: #087c72;
  font-size: 12px;
  font-weight: 900;
}

.ghost-action {
  background: rgba(255, 255, 255, 0.72);
}

.hero-board {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 1.1fr);
  align-items: stretch;
  gap: 18px;
  margin-bottom: 18px;
}

.decision-copy,
.hero-visual,
.section-card {
  border: 1px solid #e2e9ec;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.decision-copy {
  padding: 24px 28px 35px;
}

.recommendation-kicker {
  margin: 0 0 18px;
  color: #087c72;
  font-size: 16px;
  font-weight: 900;
  letter-spacing: 0;
}

.decision-copy h2 {
  margin: 0;
  color: #020819;
  font-size: 40px;
  line-height: 1.05;
  font-weight: 950;
  letter-spacing: 0;
}

.decision-reason {
  margin: 24px 0 0;
  color: #536170;
  font-size: 18px;
  line-height: 1.75;
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 26px;
}

.metric-row span {
  min-height: 112px;
  padding: 18px;
  border: 1px solid #e2e9ec;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  color: #607188;
  font-size: 14px;
}

.metric-row svg {
  display: block;
  margin-bottom: 12px;
  color: #087c72;
  font-size: 18px;
}

.metric-row b {
  display: block;
  margin-bottom: 8px;
  color: #0d1b2a;
  font-size: 26px;
  line-height: 1.1;
  font-weight: 950;
}

.metric-row small {
  display: block;
  color: #607188;
  font-size: 14px;
  line-height: 1.35;
}

.hero-actions,
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.hero-actions span {
  min-height: 34px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0 12px;
  border-radius: 4px;
  background: #f3f7fb;
  color: #1d3451;
  font-size: 15px;
  font-weight: 650;
}

.hero-actions .primary-tag {
  background: #d8ffe5;
  color: #00a05a;
  font-weight: 900;
}

.hero-visual {
  position: relative;
  overflow: hidden;
  min-height: 0;
  background: rgba(255, 255, 255, 0.86);
  display: flex;
  align-items: center;
}

.hero-visual img {
  width: 100%;
  height: 100%;
  max-height: 620px;
  object-fit: contain;
  display: block;
}

.section-card {
  margin-bottom: 18px;
  padding: 22px;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
  font-size: 24px;
}

.section-head > p {
  max-width: 460px;
  margin: 0;
  color: #607188;
  line-height: 1.7;
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.compare-card {
  overflow: hidden;
  border: 1px solid #e4ebef;
  border-radius: 8px;
  background: #fff;
}

.compare-card.active {
  border-color: rgba(8, 124, 114, 0.45);
  box-shadow: 0 14px 32px rgba(8, 124, 114, 0.12);
}

.compare-media {
  position: relative;
  height: 260px;
  padding: 16px 18px 8px;
  background:
    linear-gradient(180deg, #fbfdfc 0%, #f6faf8 100%);
}

.compare-media img {
  width: 100%;
  height: 100%;
  max-width: 86%;
  max-height: 230px;
  margin: 0 auto;
  object-fit: contain;
  object-position: center;
  display: block;
}

.evaluation-panel {
  display: grid;
  grid-template-columns: minmax(160px, 0.76fr) minmax(250px, 1fr);
  gap: 22px;
  align-items: center;
  margin-top: 24px;
  padding: 22px 24px 22px;
  border: 1px solid rgba(14, 198, 137, 0.22);
  border-radius: 8px;
  background:
    radial-gradient(circle at 84% 9%, rgba(218, 255, 241, 0.7), transparent 29%),
    linear-gradient(135deg, rgba(251, 255, 254, 0.98), rgba(248, 255, 253, 0.94));
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
}

.evaluation-content {
  min-width: 0;
}

.evaluation-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.evaluation-head > span {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #020819;
  color: #ffffff;
  font-size: 21px;
  box-shadow: 0 12px 22px rgba(2, 8, 25, 0.16);
}

.evaluation-head p {
  margin: 0 0 3px;
  color: #087c72;
  font-size: 10px;
  font-weight: 950;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

.evaluation-head h3 {
  margin: 0;
  color: #020819;
  font-size: 24px;
  line-height: 1.1;
}

.match-score {
  position: relative;
  width: 170px;
  height: 170px;
  display: grid;
  place-items: center;
  justify-self: center;
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.74) 58%, rgba(255, 255, 255, 0) 59%),
    radial-gradient(circle, rgba(8, 124, 114, 0.08), transparent 64%);
}

.match-score > svg:not(.score-icon) {
  position: absolute;
  inset: 0;
  transform: rotate(-90deg);
}

.match-score > svg:not(.score-icon) circle {
  fill: none;
  stroke-width: 4.6;
}

.match-score > svg:not(.score-icon) circle:first-child {
  stroke: #dfeae5;
}

.match-score > svg:not(.score-icon) circle:last-child {
  stroke: #087c72;
  stroke-linecap: round;
  stroke-dasharray: 301;
  stroke-dashoffset: 24;
}

.match-score strong,
.match-score small {
  position: absolute;
  left: 0;
  width: 100%;
  z-index: 1;
  display: block;
  text-align: center;
}

.match-score strong {
  top: 65px;
  color: #020819;
  font-size: 42px;
  line-height: 1;
  font-weight: 950;
}

.match-score small {
  top: 110px;
  left: 50%;
  width: auto;
  padding: 0 4px;
  background: transparent;
  color: #087c72;
  font-size: 9px;
  font-weight: 950;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  white-space: nowrap;
  transform: translateX(-50%);
}

.score-pill {
  position: absolute;
  top: -28px;
  left: 50%;
  z-index: 4;
  padding: 6px 13px;
  border: 1px solid rgba(8, 124, 114, 0.14);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  color: #087c72;
  font-size: 12px;
  font-weight: 900;
  white-space: nowrap;
  transform: translateX(-50%);
  box-shadow: 0 8px 18px rgba(8, 124, 114, 0.12);
}

.score-icon {
  position: absolute;
  top: 34px;
  left: 50%;
  z-index: 3;
  width: 30px;
  height: 30px;
  padding: 8px;
  border-radius: 50%;
  background: #dffced;
  color: #087c72;
  transform: translate(-50%, 0);
}

.score-icon path {
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.1;
}

.evaluation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.evaluation-grid section {
  min-height: 86px;
  padding: 16px 18px;
  border: 1px solid #dfe9eb;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.82);
}

.evaluation-grid svg {
  width: 28px;
  height: 28px;
  padding: 7px;
  border-radius: 50%;
  background: #e5fbf1;
  color: #087c72;
}

.evaluation-grid .sparkle-icon,
.evaluation-grid .key-icon {
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.1;
}

.evaluation-grid .key-icon {
  stroke-width: 2.3;
}

.evaluation-grid b {
  display: block;
  margin-top: 13px;
  color: #020819;
  font-size: 19px;
  line-height: 1.1;
}

.evaluation-grid p {
  margin: 6px 0 0;
  color: #607188;
  font-size: 14px;
}

.evaluation-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 12px 0 0;
  padding: 12px 20px;
  border-radius: 8px;
  background: #e8fbf1;
  color: #007a5d;
  font-size: 14px;
  font-weight: 850;
  line-height: 1.45;
}

.evaluation-note svg {
  flex: 0 0 auto;
  margin-top: 2px;
}

.compare-body {
  padding: 18px;
}

.product-label {
  margin: 0 0 8px;
  color: #087c72;
  font-weight: 900;
}

.compare-body h3,
.config-grid h3,
.source-note h3,
.phase-card h3 {
  margin: 0;
}

.compare-body > p {
  margin: 10px 0;
  color: #536170;
  line-height: 1.7;
}

ul {
  margin: 0;
  padding-left: 18px;
  color: #536170;
  line-height: 1.85;
}

@media (max-width: 1180px) {
  .evaluation-panel {
    grid-template-columns: 1fr;
  }

  .match-score {
    margin-bottom: 2px;
  }
}

.evidence-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.95fr 0.95fr;
  gap: 12px;
}

.evidence-grid figure {
  position: relative;
  min-height: 280px;
  margin: 0;
  overflow: hidden;
  border: 1px solid #e4ebef;
  border-radius: 8px;
  background: #f8faf9;
}

.evidence-grid img {
  width: 100%;
  height: 100%;
  min-height: 280px;
  object-fit: contain;
  display: block;
}

.large-shot img {
  object-fit: cover;
}

.smart-device-map {
  padding: 28px;
  background:
    radial-gradient(circle at 8% 8%, rgba(232, 241, 249, 0.95), transparent 34%),
    #f5f7fb;
}

.device-map-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
}

.device-map-header h2 {
  margin: 0;
  color: #142653;
  font-size: 28px;
  line-height: 1.18;
}

.device-map-header p {
  margin: 4px 0 0;
  color: #6c7d95;
}

.device-map-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 28px;
  align-items: stretch;
}

.figma-embed-frame {
  overflow: hidden;
  height: min(78vh, 760px);
  min-height: 560px;
  border: 1px solid #dce6f1;
  border-radius: 8px;
  background: #eef2f6;
}

.figma-embed-frame iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}

.figma-embed-note {
  margin: 12px 0 0;
  color: #6c7d95;
  font-size: 13px;
  line-height: 1.7;
}

.device-plan-column {
  min-width: 0;
}

.device-plan-title {
  margin: 0 0 14px 28px;
}

.device-plan-title strong {
  display: block;
  color: #142653;
  font-size: 14px;
  font-weight: 900;
}

.device-plan-title span {
  display: block;
  margin-top: 4px;
  color: #8390a6;
  font-size: 12px;
}

.device-plan-canvas {
  position: relative;
  overflow: hidden;
  aspect-ratio: var(--canvas-ratio);
  border-radius: 2px;
  background: #fff;
}

.device-plan-stage {
  position: absolute;
  inset: 0;
  transform: translate(var(--stage-x), var(--stage-y)) scale(var(--stage-scale));
  transform-origin: 0 0;
}

.device-plan-stage img {
  display: block;
  width: 100%;
  height: auto;
  pointer-events: none;
}

.device-dot {
  position: absolute;
  z-index: 2;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #fff;
  border-radius: 999px;
  color: #fff;
  background: var(--device-color);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.18);
  transform: translate(-50%, -50%);
}

.device-dot svg {
  width: 16px;
  height: 16px;
}

.placement-note {
  width: 80%;
  margin: 28px 0 0 28px;
  padding: 16px 18px;
  border: 1px solid #dce6f1;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.52);
  color: #6c7d95;
  line-height: 1.75;
}

.placement-note strong {
  display: block;
  margin-bottom: 4px;
  color: #142653;
  font-size: 13px;
}

.placement-note p,
.device-footnote {
  margin: 0;
  font-size: 12px;
}

.device-footnote {
  margin: 28px 0 0 28px;
  color: #9aa7b8;
}

.device-legend-card {
  padding: 28px 24px;
  border: 1px solid #dce6f1;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.78);
}

.device-legend-card h3 {
  margin: 0;
  color: #142653;
  font-size: 18px;
}

.device-legend-card > p {
  margin: 6px 0 24px;
  color: #7f8fa5;
  font-size: 12px;
}

.device-legend-card ul {
  display: grid;
  gap: 22px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.device-legend-card li {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
}

.legend-icon {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  color: #fff;
  background: var(--device-color);
}

.legend-icon svg {
  width: 16px;
  height: 16px;
}

.device-legend-card b,
.device-legend-card small {
  display: block;
}

.device-legend-card b {
  color: #25324a;
  font-size: 13px;
}

.device-legend-card small {
  margin-top: 3px;
  color: #8492a8;
  font-size: 11px;
}

.configuration-section {
  padding: 34px;
  overflow: hidden;
  border-color: #dfe9eb;
  background:
    radial-gradient(circle at 92% 18%, rgba(14, 184, 166, 0.1), transparent 22%),
    linear-gradient(180deg, #fbfefe 0%, #f7fbfa 100%);
}

.configuration-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 34px;
}

.configuration-kicker {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 18px;
  color: #087c72;
  font-size: 13px;
  font-weight: 950;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.configuration-kicker span {
  width: 30px;
  height: 6px;
  border-radius: 999px;
  background: #0fb8a6;
}

.configuration-hero h2 {
  margin: 0;
  color: #020819;
  font-size: 54px;
  line-height: 1;
  font-weight: 950;
}

.configuration-hero p:last-child {
  margin: 20px 0 0;
  color: #607188;
  font-size: 17px;
  line-height: 1.7;
}

.generated-badge {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 8px;
  min-height: 36px;
  padding: 0 18px;
  border: 1px solid rgba(15, 184, 166, 0.2);
  border-radius: 999px;
  background: rgba(232, 255, 249, 0.7);
  color: #087c72;
  font-size: 14px;
  font-weight: 900;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.config-card {
  min-height: 190px;
  padding: 24px;
  border: 1px solid #dfe9eb;
  border-radius: 8px;
  background:
    radial-gradient(circle at 94% 8%, rgba(14, 184, 166, 0.09), transparent 30%),
    rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.06);
}

.config-card-title {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
}

.config-card-title > span {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #05aa91;
  color: #ffffff;
  font-size: 23px;
  box-shadow: 0 12px 22px rgba(5, 170, 145, 0.22);
}

.config-card-title h3 {
  margin: 0;
  color: #020819;
  font-size: 28px;
  line-height: 1.1;
  font-weight: 950;
}

.module-chip-list,
.smart-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.module-chip,
.smart-chip {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.module-chip {
  border: 1px solid #dfe8ee;
  background: #ffffff;
  color: #596a80;
}

.smart-chip {
  border: 1px solid rgba(5, 170, 145, 0.22);
  background: rgba(232, 255, 249, 0.8);
  color: #087c72;
}

.module-chip svg,
.smart-chip svg {
  flex: 0 0 auto;
  color: #087c72;
  font-size: 16px;
}

.list-card,
.basis-card {
  min-height: 420px;
}

.configuration-items-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.configuration-item {
  min-height: 66px;
  display: grid;
  grid-template-columns: 36px 1fr;
  align-items: center;
  gap: 12px;
  padding: 13px 14px;
  border-radius: 8px;
  background: #f7faf9;
}

.configuration-item > span {
  width: 31px;
  height: 31px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #ffffff;
  color: #087c72;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
}

.configuration-item p,
.basis-item p {
  margin: 0;
  color: #53657b;
  font-size: 16px;
  line-height: 1.55;
  font-weight: 650;
}

.basis-list {
  display: grid;
  gap: 16px;
}

.basis-item {
  min-height: 78px;
  display: grid;
  grid-template-columns: 38px 1fr;
  align-items: start;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e7eef1;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.82);
}

.basis-item > span {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #020819;
  color: #ffffff;
  font-weight: 950;
}

.value-grid article,
.phase-card,
.boundary-section article {
  padding: 16px;
  border: 1px solid #e4ebef;
  border-radius: 8px;
  background: #f8faf9;
}

.value-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.value-grid span {
  display: block;
  margin-bottom: 16px;
  color: #f482a6;
  font-weight: 900;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.value-grid strong {
  display: block;
  color: #0d1b2a;
}

.value-grid p {
  margin: 8px 0 0;
  color: #607188;
  font-size: 13px;
  line-height: 1.65;
}

.delivery-board {
  display: grid;
  grid-template-columns: repeat(7, minmax(168px, 1fr));
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.phase-card {
  min-height: 272px;
}

.phase-card > span {
  display: block;
  margin-bottom: 12px;
  color: #f482a6;
  font-weight: 900;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.phase-card h3 {
  color: #0d1b2a;
  font-size: 16px;
}

.phase-card p {
  margin: 10px 0 0;
  color: #536170;
  font-size: 13px;
  line-height: 1.55;
}

.phase-card strong {
  display: block;
  color: #087c72;
}

.boundary-section {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 14px;
}

.source-note {
  background: #eef8f4 !important;
}

.source-note p,
.source-note strong {
  display: block;
  margin: 10px 0 0;
  color: #536170;
  line-height: 1.75;
}

@media (max-width: 960px) {
  .page-header,
  .hero-board,
  .compare-grid,
  .evidence-grid,
  .config-grid,
  .value-grid,
  .boundary-section {
    grid-template-columns: 1fr;
  }

  .section-head {
    display: block;
  }

  .section-head > p {
    margin-top: 8px;
  }

  .configuration-section {
    padding: 22px;
  }

  .configuration-hero {
    display: block;
  }

  .configuration-hero h2 {
    font-size: 40px;
  }

  .generated-badge {
    margin-top: 18px;
  }

  .configuration-items-grid {
    grid-template-columns: 1fr;
  }

  .metric-row {
    grid-template-columns: 1fr;
  }

  .smart-device-map {
    padding: 20px;
  }

  .device-map-header,
  .device-map-layout {
    display: block;
  }

  .device-map-header .arco-btn {
    margin-top: 12px;
  }

  .device-plan-title,
  .placement-note,
  .device-footnote {
    margin-left: 0;
  }

  .device-dot {
    width: 26px;
    height: 26px;
    border-width: 2px;
  }

  .device-dot svg {
    width: 13px;
    height: 13px;
  }

  .placement-note {
    width: auto;
  }

  .device-legend-card {
    margin-top: 18px;
  }
}
</style>
