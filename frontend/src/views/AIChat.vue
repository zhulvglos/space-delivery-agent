<template>
  <main class="ai-chat-page">
    <header class="page-header">
      <div class="header-copy">
        <p class="eyebrow hero-pill"><IconThunderbolt />双 Agent PoC / LLM + 规则护栏</p>
        <h1>创建配置方案 / 生成交付看板</h1>
        <p>案例来源：瑞泽·海度假民宿已建项目复盘，产品体系为卡素 Capsule Cabin</p>
      </div>
      <div class="header-right">
        <a-button class="back-btn" @click="$router.push('/home')"><IconArrowLeft />返回</a-button>
        <a-button type="primary" class="project-btn" @click="openProjectDetail()">查看方案页</a-button>
      </div>
    </header>

    <section class="workspace">
      <aside class="templates">
        <div class="side-heading">
          <h2>快捷模板</h2>
          <span>{{ templates.length }} presets</span>
        </div>
        <button v-for="(template, index) in templates" :key="template" class="template-card" @click="useTemplate(template)">
          <span class="template-index">Template {{ String(index + 1).padStart(2, '0') }}</span>
          <span class="template-text">{{ template }}</span>
          <IconArrowRight class="template-arrow" />
        </button>
        <div class="demo-note">
          <span class="demo-icon"><IconTool /></span>
          <strong>PoC 边界</strong>
          <p>当前版本支持 LLM + 规则护栏：配置 API Key 后由 LLM 生成方案与看板，未配置或调用失败时自动规则兜底。</p>
        </div>
      </aside>

      <section class="chat-panel">
        <div class="panel-metrics">
          <section>
            <span class="metric-icon"><IconLayers /></span>
            <div>
              <p>空间模块</p>
              <strong>38㎡ / 56㎡</strong>
            </div>
          </section>
          <section>
            <span class="metric-icon"><IconRobot /></span>
            <div>
              <p>Agent 编排</p>
              <strong>双 Agent</strong>
            </div>
          </section>
          <section>
            <span class="metric-icon"><IconSafe /></span>
            <div>
              <p>规则护栏</p>
              <strong>LLM + API</strong>
            </div>
          </section>
        </div>
        <div class="message-list" ref="chatContainer">
          <section v-if="messages.length === 0" class="empty-guide">
            <p class="eyebrow guide-pill"><IconThunderbolt />体验路径</p>
            <h2>从业主需求到配置方案，再到交付看板</h2>
            <div class="agent-flow-strip">
              <span>需求输入</span>
              <span>空间配置 Agent</span>
              <span>配置方案</span>
              <span>交付规划 Agent</span>
              <span>交付看板</span>
            </div>
            <ol>
              <li><IconCheckCircle /><b>1.</b><span>选择左侧快捷模板，模拟业主方扩建需求输入。</span></li>
              <li><IconCheckCircle /><b>2.</b><span>空间配置 Agent 基于瑞泽·海项目复盘规则推荐 38㎡ / 56㎡产品。</span></li>
              <li><IconCheckCircle /><b>3.</b><span>查看空间模块、标配/选配、智能设备与推荐依据。</span></li>
              <li><IconCheckCircle /><b>4.</b><span>点击生成交付规划，得到 7 阶段交付任务、验收点与风险提示。</span></li>
            </ol>
            <p class="guide-note">亮点：展示“需求输入 → 需求解析 → 产品匹配 → 配置方案 → 交付任务”的 Agent 工作流。配置 LLM 后会显示“LLM 已调用”，失败时保留规则型兜底。</p>
          </section>
          <div v-for="msg in messages" :key="msg.id" :data-message-id="msg.id" :class="['message', msg.role]">
            <div class="message-label">{{ msg.role === 'user' ? '需求输入' : msg.agent === 'delivery_planning' ? '交付规划 Agent' : '空间配置 Agent' }}</div>
            <div class="message-body" v-html="renderMarkdown(msg.content)"></div>

            <article v-if="msg.agent_trace" class="agent-trace-card">
              <div class="trace-head">
                <div>
                  <p class="trace-kicker">{{ msg.agent_trace.mode }}</p>
                  <h3>{{ msg.agent_trace.title }}</h3>
                </div>
                <span>{{ msg.agent_trace.confidence }}</span>
              </div>

              <div class="trace-grid">
                <section class="trace-panel">
                  <h4>需求解析</h4>
                  <div class="signal-list">
                    <span v-for="signal in msg.agent_trace.signals" :key="signal.label">
                      <b>{{ signal.label }}</b>{{ signal.value }}
                    </span>
                  </div>
                </section>
                <section class="trace-panel">
                  <h4>规则命中</h4>
                  <ul>
                    <li v-for="rule in msg.agent_trace.rules" :key="rule">{{ rule }}</li>
                  </ul>
                </section>
              </div>

              <div class="agent-steps">
                <article v-for="step in msg.agent_trace.steps" :key="step.name">
                  <span>{{ step.index }}</span>
                  <strong>{{ step.name }}</strong>
                  <p>{{ step.detail }}</p>
                </article>
              </div>
            </article>

            <article v-if="msg.generated_plan" class="result-card">
              <div class="card-title">
                <span>空间配置方案</span>
                <a-button type="primary" size="small" @click="generateDelivery(msg.generated_plan)">生成交付规划</a-button>
              </div>
              <section v-if="msg.generated_plan.llm_insights || msg.generation_mode === 'llm_with_rule_guardrails'" class="llm-insight-card">
                <div class="llm-insight-head">
                  <span>LLM 已调用</span>
                  <small>{{ msg.llm_provider || msg.generated_plan.llm_provider || 'anthropic' }} + 规则护栏</small>
                </div>
                <p>{{ msg.generated_plan.llm_insights?.summary || 'LLM 已在真实项目复盘规则约束下复核方案，并补充业主侧判断。' }}</p>
                <div class="llm-insight-grid">
                  <section>
                    <h4>待确认问题</h4>
                    <ul>
                      <li v-for="item in msg.generated_plan.llm_insights?.owner_questions || []" :key="item">{{ item }}</li>
                    </ul>
                  </section>
                  <section>
                    <h4>取舍建议</h4>
                    <ul>
                      <li v-for="item in msg.generated_plan.llm_insights?.tradeoffs || []" :key="item">{{ item }}</li>
                    </ul>
                  </section>
                </div>
              </section>
              <a-descriptions :column="2" size="small" bordered>
                <a-descriptions-item label="推荐产品">{{ msg.generated_plan.recommended_product }}</a-descriptions-item>
                <a-descriptions-item label="面积">{{ msg.generated_plan.recommended_area_sqm }}㎡</a-descriptions-item>
                <a-descriptions-item label="客群">{{ msg.generated_plan.target_guests }}</a-descriptions-item>
                <a-descriptions-item label="运营">{{ msg.generated_plan.operation_mode }}</a-descriptions-item>
              </a-descriptions>
              <div class="chips">
                <a-tag v-for="item in msg.generated_plan.space_modules" :key="item">{{ item }}</a-tag>
              </div>
              <h3>配置清单</h3>
              <ul>
                <li v-for="item in msg.generated_plan.configuration_items" :key="item">{{ item }}</li>
              </ul>
              <h3>智能设备</h3>
              <div class="chips">
                <a-tag v-for="item in msg.generated_plan.smart_devices" :key="item" color="green">{{ item }}</a-tag>
              </div>
              <h3>推荐依据</h3>
              <ul>
                <li v-for="item in msg.generated_plan.recommendation_basis" :key="item">{{ item }}</li>
              </ul>
              <h3>数据来源</h3>
              <p class="budget-note">{{ msg.generated_plan.data_source_note }}</p>
              <p class="budget-note">{{ msg.generated_plan.budget_range?.note }}</p>
              <section v-if="msg.generated_plan.upgrade_delta" class="upgrade-delta-card">
                <h3>本次升级差异</h3>
                <p>{{ msg.generated_plan.upgrade_delta.summary }}</p>
                <div class="upgrade-grid">
                  <section>
                    <h4>新增设备</h4>
                    <ul>
                      <li v-for="item in msg.generated_plan.upgrade_delta.added_devices" :key="item">{{ item }}</li>
                    </ul>
                  </section>
                  <section>
                    <h4>调试风险</h4>
                    <ul>
                      <li v-for="item in msg.generated_plan.upgrade_delta.commissioning_risks" :key="item">{{ item }}</li>
                    </ul>
                  </section>
                  <section>
                    <h4>验收点</h4>
                    <ul>
                      <li v-for="item in msg.generated_plan.upgrade_delta.acceptance_points" :key="item">{{ item }}</li>
                    </ul>
                  </section>
                </div>
              </section>
            </article>

            <article v-if="msg.generated_delivery && msg.generated_delivery.intent === 'risk_assessment'" class="result-card">
              <div class="card-title">
                <span>场地风险评估</span>
                <a-button size="small" @click="openProjectDetail(msg.generated_delivery)">打开详情</a-button>
              </div>
              <div class="risk-list">
                <section v-for="risk in msg.generated_delivery.site_risks" :key="risk.risk" class="risk-item" :class="'severity-' + risk.severity">
                  <div class="risk-header">
                    <span class="risk-category">{{ risk.category }}</span>
                    <span class="risk-severity">{{ risk.severity }}</span>
                  </div>
                  <p class="risk-desc">{{ risk.risk }}</p>
                  <p class="risk-mitigation"><strong>应对：</strong>{{ risk.mitigation }}</p>
                  <p class="risk-owner"><strong>确认方：</strong>{{ risk.confirmation_owner }}</p>
                </section>
              </div>
              <div v-if="msg.generated_delivery.pre_confirmation_items?.length" class="pre-confirm-list">
                <h3>开工前必须确认事项</h3>
                <ul>
                  <li v-for="item in msg.generated_delivery.pre_confirmation_items" :key="item">{{ item }}</li>
                </ul>
              </div>
            </article>

            <article v-if="msg.generated_delivery && msg.generated_delivery.intent !== 'risk_assessment'" class="result-card">
              <div class="card-title">
                <span>交付看板</span>
                <a-button size="small" @click="openProjectDetail(msg.generated_delivery)">打开详情</a-button>
              </div>
              <div class="phase-list">
                <section v-for="phase in msg.generated_delivery.delivery_phases" :key="phase.phase" class="phase-item">
                  <h3>{{ phase.phase }}</h3>
                  <p><strong>任务：</strong>{{ phase.tasks.join('、') }}</p>
                  <p><strong>验收：</strong>{{ phase.acceptance_criteria.join('、') }}</p>
                  <p><strong>风险：</strong>{{ phase.risks.join('、') }}</p>
                </section>
              </div>
            </article>
          </div>
          <div v-if="loading" class="message assistant">
            <div class="message-label">Agent</div>
            <div class="message-body">正在调用 LLM，并用项目复盘规则校验输出...</div>
          </div>
        </div>

        <footer class="input-area">
          <a-textarea v-model="inputMessage" placeholder="描述民宿扩建需求，或点击左侧快捷模板" :auto-size="{ minRows: 3, maxRows: 5 }" />
          <div class="input-actions">
            <a-button @click="clearMessages">清空</a-button>
            <a-button type="primary" :disabled="!inputMessage.trim() || loading" @click="handleSend">发送 <IconSend /></a-button>
          </div>
        </footer>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconArrowLeft,
  IconArrowRight,
  IconCheckCircle,
  IconLayers,
  IconRobot,
  IconSafe,
  IconSend,
  IconThunderbolt,
  IconTool
} from '@arco-design/web-vue/es/icon'
import { agentApi } from '../api/agent'

const templates = [
  '基于瑞泽·海度假民宿复盘，为滨海度假区新增一套 38㎡卡素单体产品，自助入住，配置基础智能控制。',
  '为 6 人亲子/小团体入住场景推荐卡素 56㎡拼装产品，要求保留活动区和简餐区，并配置自助入住。',
  '基于上一轮已确认配置，生成 7 阶段装配式交付看板。',
  '滨海场地道路较窄、吊装空间有限，评估该场景下的交付风险与前置确认项。'
]

const inputMessage = ref('')
const loading = ref(false)
const chatContainer = ref<HTMLElement>()
const messages = ref<any[]>([])
const latestConfiguration = ref<any>(null)

const extractGuestCount = (message: string) => {
  const text = message || ''
  const digitMatch = text.match(/(\d+)\s*(个人|人|位|名|口)/)
  if (digitMatch) return Number(digitMatch[1])
  const chineseDigits: Record<string, number> = {
    一: 1,
    二: 2,
    两: 2,
    三: 3,
    四: 4,
    五: 5,
    六: 6,
    七: 7,
    八: 8,
    九: 9,
    十: 10,
  }
  const chineseMatch = text.match(/([一二两三四五六七八九十])\s*(个人|人|位|名|口)/)
  return chineseMatch ? chineseDigits[chineseMatch[1]] : null
}

const shouldUseFamilyProduct = (message: string) => {
  const guestCount = extractGuestCount(message)
  return Boolean(
    (guestCount && guestCount > 4) ||
    message.includes('亲子') ||
    message.includes('家庭') ||
    message.includes('小团体') ||
    message.includes('多人') ||
    message.includes('56') ||
    message.includes('做饭') ||
    message.includes('活动区') ||
    message.includes('宽松') ||
    message.includes('灵活')
  )
}

const createRuleBasedConfiguration = (message: string) => {
  const guestCount = extractGuestCount(message)
  const guestOverLimit = Boolean(guestCount && guestCount > 4)
  const isFamily = shouldUseFamilyProduct(message)
  const scoreS = isFamily ? 0 : 3
  const scoreM = isFamily ? 5 : 0
  return {
    project_name: isFamily ? '瑞泽·海度假民宿 56㎡拼装配置（规则型 PoC）' : '瑞泽·海度假民宿 38㎡单体扩建（规则型 PoC）',
    real_project_name: '瑞泽·海度假民宿',
    product_system: '卡素产品体系 / Capsule Cabin',
    recommended_product: isFamily ? 'Capsule Cabin M' : 'Capsule Cabin S',
    recommended_area_sqm: isFamily ? 56 : 38,
    recommendation_reason: isFamily
      ? guestCount && guestCount > 4
        ? `输入中包含 ${guestCount} 人入住，已超过 38㎡单体最多 4 人的舒适接待边界，优先匹配 56㎡拼装产品；仍需人工确认是否采用单套 56㎡、双套组合或加床策略。`
        : '输入中包含多人入住、做饭、活动区或空间宽松需求，匹配瑞泽·海项目复盘中 56㎡拼装产品的适用场景。'
      : '输入以单体扩建、面积控制或标准房型为主，匹配瑞泽·海项目中 38㎡单体产品的紧凑型配置经验；该产品最多可支持 4 人入住。',
    recommendation_basis: [
      isFamily ? (guestCount && guestCount > 4 ? `${guestCount} 人入住超过 38㎡单体建议上限，56㎡拼装作为最低优先方案，并建议继续确认是否需要组合多套。` : '56㎡拼装产品解决多人入住、活动区、做饭和空间灵活变换问题。') : '38㎡单体产品空间紧凑，不严格限定客群，最多 4 人入住。',
      '偏无人化运营关注入住效率、维护成本、拍照传播和舒适度。',
      '自助入住场景需要智能门锁、灯光、空调、窗帘、传感器、监控与稳定网络。',
      '滨海场地需要提前关注防腐、防水、潮湿、风、排水、供电网络和吊装条件。'
    ],
    target_guests: isFamily ? (guestCount && guestCount > 4 ? `${guestCount} 人入住 / 需确认组合接待` : '多人入住 / 亲子 / 小团体') : '不限定客群，空间紧凑，最多 4 人入住',
    style: '柔和粉白色系，海滨轻度假',
    operation_mode: '偏无人化运营，自助入住 + 基础智能控制',
    intelligence_level: message.includes('更高') ? '标准' : '基础',
    space_modules: isFamily
      ? ['睡眠区', '卫浴', '活动区', '简餐/烹饪区', '水吧台', '收纳区', '灵活变换区']
      : ['榻榻米', '衣柜/挂衣空间', '卫浴', '沙发区', '水吧台', '换鞋区'],
    configuration_items: ['床和品质较好的床垫', '床头柜、写字台、座椅、茶几', '衣橱/挂衣空间、衣架、行李架', '干湿分离卫浴', '24小时冷水/定时热水', '电热水壶、茶包/咖啡、瓶装水', '空调/供暖设备', '220V电源插座', '烟雾报警器等消防设施', '稳定 Wi-Fi、电视'],
    smart_devices: ['智能门锁', '灯光控制', '空调控制', '窗帘控制', '传感器', '监控', '稳定 Wi-Fi'],
    data_source_note: '基于瑞泽·海度假民宿已建项目参与经验、产品资料图、户型图与现场交付复盘整理；非合同、报价或正式工程记录。',
    budget_range: { level: '中档', note: '示例配置预算区间，仅用于规则型 PoC 演示，不构成正式报价。' },
    decision_score: {
      product_vote: isFamily ? '56㎡' : '38㎡',
      score_s: scoreS,
      score_m: scoreM,
      confidence: isFamily ? 0.83 : 0.75,
      signals: [
        { dimension: '入住场景', value: guestCount ? `${guestCount} 人` : '标准客房', reason: guestOverLimit ? '超过单体舒适边界' : '单体可满足', confidence: guestOverLimit ? 0.9 : 0.7 },
        { dimension: '面积倾向', value: isFamily ? '56㎡拼装' : '38㎡单体', reason: isFamily ? '多人/活动区/做饭关键词命中' : '未命中扩展关键词', confidence: isFamily ? 0.85 : 0.7 },
        { dimension: '运营方式', value: '自助入住（默认）', reason: '按案例默认自助入住 + 基础智能', confidence: 0.75 },
        { dimension: '智能化等级', value: message.includes('更高') || message.includes('标准') || message.includes('智能') ? '标准智能化' : '基础', reason: message.includes('更高') ? '用户明确要求升级' : '默认基础', confidence: message.includes('更高') ? 0.9 : 0.65 },
      ],
      recommended_product: isFamily ? 'Capsule Cabin M' : 'Capsule Cabin S',
    }
  }
}

const createIntelligenceUpgradePlan = (configuration: any) => {
  const base = configuration || createRuleBasedConfiguration('38㎡卡素单体产品')
  const addedDevices = ['全屋智能客控系统', '大屏幕投影设备', '入住/离房场景联动', '温湿度或人体存在传感器', '远程运维监测']
  const upgradedConfigurationItems = [...(base.configuration_items || [])]
  addedDevices.slice(0, 2).forEach((item) => {
    if (!upgradedConfigurationItems.includes(item)) upgradedConfigurationItems.push(item)
  })
  const upgradedSmartDevices = [...(base.smart_devices || [])]
  addedDevices.forEach((item) => {
    if (!upgradedSmartDevices.includes(item)) upgradedSmartDevices.push(item)
  })
  return {
    ...base,
    project_name: `${base.project_name || '瑞泽·海度假民宿配置方案'}｜标准智能化升级`,
    operation_mode: '偏无人化运营，自助入住 + 标准智能控制',
    intelligence_level: '标准',
    configuration_items: upgradedConfigurationItems,
    smart_devices: upgradedSmartDevices,
    budget_range: { ...(base.budget_range || {}), level: '中高档', note: '示例配置预算区间，仅用于标准智能化升级 PoC 演示，不构成正式报价。' },
    recommendation_reason: `本次不是重新选型，而是在已确认的 ${base.recommended_product} / ${base.recommended_area_sqm}㎡ 方案上，把智能化等级从基础升级到标准。`,
    upgrade_delta: {
      type: 'intelligence_level_upgrade',
      from_level: '基础',
      to_level: '标准',
      kept_product: base.recommended_product,
      kept_area_sqm: base.recommended_area_sqm,
      summary: `保留 ${base.recommended_product} / ${base.recommended_area_sqm}㎡ 的空间方案，只升级智能化配置与验收要求。`,
      added_devices: addedDevices,
      commissioning_risks: [
        '门锁、灯光、空调、窗帘和传感器联动逻辑需要现场逐项测试。',
        '标准智能化更依赖网络稳定性，弱电到货、布线和信号覆盖要前置确认。',
        '自助入住链路故障会直接影响运营体验，需要保留人工应急开门和设备重置方案。',
      ],
      acceptance_points: [
        '完成门锁到灯光、空调、窗帘的入住场景联调。',
        '验证离房节能、异常告警和远程重置能力。',
        '检查监控覆盖、隐私边界和网络回传稳定性。',
        '形成智能设备点位、账号权限和运维交接清单。',
      ],
    },
  }
}

const inferDemandSignals = (message: string, plan?: any) => {
  const text = message || ''
  const guestCount = extractGuestCount(text)
  const familyKeywords = ['亲子', '家庭', '小团体', '多人', '56', '做饭', '活动区', '宽松', '灵活']
  const intelligenceKeywords = ['智能', '更高', '标准', '无人', '自助']
  return [
    { label: '入住场景', value: guestCount && guestCount > 4 ? `${guestCount} 人入住，超过单体舒适边界` : familyKeywords.some((keyword) => text.includes(keyword)) ? '多人 / 亲子 / 小团体倾向' : '标准客房 / 单体扩建倾向' },
    { label: '面积倾向', value: text.includes('56') || plan?.recommended_area_sqm === 56 ? '56㎡拼装' : text.includes('38') || plan?.recommended_area_sqm === 38 ? '38㎡单体' : '未明确，由产品规则推断' },
    { label: '运营方式', value: text.includes('自助') || text.includes('无人') ? '偏无人化运营' : '按案例默认自助入住' },
    { label: '智能等级', value: text.includes('更高') || text.includes('标准') || text.includes('智能') ? '标准智能化' : '基础智能控制' }
  ]
}

const resolveTraceMode = (generationMode?: string, provider?: string) => {
  if (generationMode === 'llm_with_rule_guardrails') {
    return `LLM + 规则护栏 Agent Trace${provider ? ` / ${provider}` : ''}`
  }
  if (generationMode === 'frontend_rule_fallback') return '本地规则兜底 Agent Trace'
  return '规则型 Agent Trace'
}

const buildSpaceAgentTrace = (message: string, plan: any, generationMode?: string, provider?: string) => {
  const selectedM = plan?.recommended_area_sqm >= 56
  const usedFallback = generationMode === 'frontend_rule_fallback' || plan?.generation_mode === 'frontend_rule_fallback'
  const ds = plan?.decision_score
  const scoreSignals = ds?.signals?.map((s: any) => ({ label: s.dimension, value: `${s.value}  ${s.reason}` })) || []
  const signalList = scoreSignals.length ? scoreSignals : inferDemandSignals(message, plan)
  return {
    mode: resolveTraceMode(generationMode || plan?.generation_mode, provider || plan?.llm_provider),
    title: '空间配置 Agent 如何得到这个方案',
    confidence: generationMode === 'llm_with_rule_guardrails' || plan?.generation_mode === 'llm_with_rule_guardrails'
      ? 'LLM 已调用'
      : usedFallback ? 'LLM 超时/失败，已兜底'
      : ds ? `评分：38㎡=${ds.score_s} vs 56㎡=${ds.score_m}，置信度=${ds.confidence}`
      : selectedM ? '候选匹配：M 型优先' : '候选匹配：S 型优先',
    signals: signalList,
    rules: [
      selectedM
        ? '命中”多人 / 做饭 / 活动区 / 空间宽松”关键词，优先推荐 56㎡拼装产品。'
        : '未命中多人扩展关键词，按单体扩建和面积控制规则推荐 38㎡单体产品。',
      '运营侧默认采用瑞泽·海复盘中的”自助入住 + 基础智能控制”。',
      '滨海场地自动追加防腐、防水、潮湿、风、排水、供电网络和吊装条件约束。',
      '所有配置项来自卡素 Capsule Cabin 产品资料和已建项目复盘，不作为正式报价。'
    ],
    steps: [
      { index: '01', name: '解析业主输入', detail: ds ? '通过评分表逐项评估入住人数、餐区、活动区、智能等级、预算等 7 个维度。' : '抽取面积、入住人数、运营方式、智能化等级等需求信号。' },
      { index: '02', name: '匹配产品模型', detail: ds ? `综合评分 38㎡=${ds.score_s}，56㎡=${ds.score_m}，${ds.product_vote} 胜出。` : '在 Capsule Cabin S / M 两个候选中根据规则选择推荐户型。' },
      { index: '03', name: '生成配置清单', detail: '组合空间模块、家具软装、卫浴机电、智能设备和预算层级。' },
      { index: '04', name: '标记待确认项', detail: '把面积、BOM、现场条件和审批安全项留给人工确认。' }
    ]
  }
}

const buildDeliveryAgentTrace = (configuration: any, delivery: any, generationMode?: string, provider?: string) => {
  const usedFallback = generationMode === 'frontend_rule_fallback' || delivery?.generation_mode === 'frontend_rule_fallback'
  const area = configuration?.recommended_area_sqm || delivery?.recommended_area_sqm || 38
  const intel = configuration?.intelligence_level || delivery?.intelligence_level || '基础'
  const isM = area >= 56
  const isRiskAssessment = delivery?.intent === 'risk_assessment'
  return {
    mode: resolveTraceMode(generationMode || delivery?.generation_mode, provider || delivery?.llm_provider),
    title: isRiskAssessment ? '交付规划 Agent 如何评估场地风险' : '交付规划 Agent 如何拆成看板',
    confidence: generationMode === 'llm_with_rule_guardrails' || delivery?.generation_mode === 'llm_with_rule_guardrails'
      ? 'LLM 已调用'
      : usedFallback ? 'LLM 超时/失败，已兜底'
      : isRiskAssessment ? `${delivery?.site_risks?.length || 4} 项风险评估` : `${delivery?.delivery_phases?.length || 7} 阶段交付拆解`,
  signals: [
    { label: '接收产品', value: configuration?.recommended_product || delivery?.recommended_product || 'Capsule Cabin S' },
    { label: '面积口径', value: `${area}㎡` },
    { label: '智能化等级', value: intel },
    { label: '产品类型', value: isM ? '拼装（多模块）' : '单体' },
    { label: '场地约束', value: '滨海 / 吊装 / 防腐防水 / 供电网络' },
  ],
  rules: [
    '以已确认配置作为输入，不重新推荐产品，避免配置与交付看板不一致。',
    isRiskAssessment ? '风险评估聚焦道路运输、吊装空间、滨海防腐防水、供电网络和人工确认项。' : '交付阶段按设计确认、工厂预制、运输、现场基础、吊装、拼接安装、调试验收拆分。',
    isM ? '56㎡拼装产品：强化工厂批次管理、拼接精度、密封/防水/隔音验收和现场协调。' : '38㎡单体产品：按标准单体流程推进。',
    intel === '标准' ? '标准智能化等级：强化传感器联调、联网场景测试和自助入住全链路验收。' : '基础智能控制：按基础设备调试流程推进。',
    '高风险环节来自复盘规则：工厂加工/预制、拼接安装、调试验收。',
    '所有阶段都保留 human_confirmation_required，强调工程和审批必须人工确认。'
  ],
  steps: [
    { index: '01', name: '读取配置', detail: '接收空间配置 Agent 生成的产品、面积、智能化等级和现场条件。' },
    { index: '02', name: isRiskAssessment ? '识别场地约束' : '拆交付阶段', detail: isRiskAssessment ? '抽取道路较窄、吊装空间有限、滨海等约束信号。' : isM ? '基于 56㎡拼装产品特性，动态扩充工厂批次管理、拼接精度和密封防水任务。' : '把单体装配交付拆成可执行的阶段任务。' },
    { index: '03', name: isRiskAssessment ? '评估风险等级' : '补验收标准', detail: isRiskAssessment ? '按运输、吊装、防腐防水、供电网络分级输出应对策略。' : intel === '标准' ? '在调试验收阶段追加传感器联调、自助入住场景全链路验证。' : '为每个阶段生成验收点和人工确认要求。' },
    { index: '04', name: '标记人工确认', detail: isRiskAssessment ? '输出开工前必须确认的道路、吊装、基础、供电和审批项。' : '前置滨海、防腐、防水、运输、吊装和调试风险。' }
    ]
  }
}

const createRuleBasedDelivery = (configuration: any) => ({
  project_name: configuration?.project_name || '瑞泽·海度假民宿 38㎡单体扩建（规则型 PoC）',
  real_project_name: configuration?.real_project_name || '瑞泽·海度假民宿',
  recommended_product: configuration?.recommended_product || 'Capsule Cabin S',
  recommended_area_sqm: configuration?.recommended_area_sqm || 38,
  delivery_phases: [
    ['设计确认', ['生成业主方需求问卷', '确认产品型号、面积和入住人数边界', '确认标配/选配和智能化等级'], ['形成已确认配置表', '关键需求进入面积与 BOM 控制清单'], ['需求端信息不完整会影响后续设计、BOM 和生产排期']],
    ['工厂加工/预制', ['按确认方案进入工厂加工', '核对模块尺寸、材料、家具和智能设备预留', '跟踪材料到货与生产进度'], ['BOM 与配置表一致', '关键预留点位完成出厂检查'], ['材料到货、尺寸偏差和预留点位会影响现场安装']],
    ['运输', ['核对运输尺寸', '确认道路条件与到场时间', '确认包装保护和临停空间'], ['运输尺寸、道路条件和到场窗口经人工确认'], ['道路运输、限高、转弯半径和现场临停条件可能影响到场']],
    ['现场基础', ['检查基础平整度', '确认排水、防水、防腐条件', '确认供电网络预留'], ['基础、排水、防水、防腐、供电网络达到安装前置条件'], ['基础不平、排水、防水、防腐和供电网络是关键问题']],
    ['吊装', ['确认吊装空间', '按单体逐套推进吊装', '确认风力和现场安全条件'], ['吊装作业面、吊装顺序和现场安全条件经人工确认'], ['滨海场地需关注风、吊装空间和现场安全']],
    ['拼接安装', ['完成模块拼接', '检查连接、密封、防水节点', '核对隔音、隐私和空调体验'], ['拼接节点、密封、防水和室内体验问题完成检查'], ['拼接精度、防水、隔音、隐私和空调容易被忽略']],
    ['调试验收', ['调试智能门锁、灯光、空调、窗帘、传感器、监控和网络', '核对配置清单', '整理验收问题清单'], ['智能设备可用', '网络和供电稳定', '形成验收记录'], ['设备调试、网络和供电稳定性会影响无人化运营体验']]
  ].map(([phase, tasks, acceptance_criteria, risks]) => ({
    phase,
    tasks,
    acceptance_criteria,
    risks,
    human_confirmation_required: true
  })),
  site_risks: [
    '滨海环境风险：防腐、防水、潮湿、风。',
    '现场交付条件：吊装空间、道路运输、基础不平、排水、防水、防腐、供电网络需提前确认。',
    '现场施工最大风险之一是材料到货，需联动 BOM 与生产进度。',
    '室内体验易忽略隔音、隐私和空调，需要进入验收清单。',
    '消防、结构、安全和审批要求不由 PoC 自动确认。'
  ],
  high_risk_phases: ['工厂加工/预制', '拼接安装', '调试验收'],
  data_source_note: '基于瑞泽·海度假民宿已建项目参与经验、产品资料图、户型图与现场交付复盘整理。'
})

const buildProjectSnapshot = (configuration?: any, delivery?: any) => {
  const currentConfig = configuration || latestConfiguration.value || (
    delivery?.recommended_area_sqm
      ? createRuleBasedConfiguration(`${delivery.recommended_area_sqm}㎡ ${delivery.recommended_product || ''}`)
      : null
  )
  const area = currentConfig?.recommended_area_sqm || 38
  const normalizedDelivery = delivery?.intent === 'risk_assessment'
    ? {
        ...createRuleBasedDelivery(currentConfig),
        risk_assessment: delivery,
      }
    : delivery
  return {
    title: currentConfig?.project_name || (area >= 56 ? '瑞泽·海度假民宿 56㎡拼装配置（规则型 PoC）' : '瑞泽·海度假民宿 38㎡单体扩建（规则型 PoC）'),
    data_source_note: currentConfig?.data_source_note || '基于瑞泽·海度假民宿已建项目参与经验、产品资料图、户型图与现场交付复盘整理；非合同、报价或正式工程记录。',
    disclaimer: '本案例为基于瑞泽·海度假民宿已建项目经验复盘的规则型 AI PoC；配置、预算与周期均为示例，不构成正式设计、报价或施工承诺。',
    configuration: currentConfig || createRuleBasedConfiguration('38㎡卡素单体产品'),
    delivery: normalizedDelivery || createRuleBasedDelivery(currentConfig)
  }
}

const saveProjectSnapshot = (configuration?: any, delivery?: any) => {
  window.localStorage.setItem('capsule_cabin_current_project', JSON.stringify(buildProjectSnapshot(configuration, delivery)))
}

const openProjectDetail = (delivery?: any) => {
  saveProjectSnapshot(latestConfiguration.value, delivery)
  window.location.href = '/project/demo-capsule-cabin'
}

const renderMarkdown = (content: string) =>
  content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')

const demoChatWithFastFallback = (payload: any) =>
  Promise.race([
    agentApi.demoChat(payload),
    new Promise((_, reject) => window.setTimeout(() => reject(new Error('规则兜底')), 170000))
  ])

const scrollToBottom = () => nextTick(() => {
  if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
})

const scrollToMessage = (messageId: string) => nextTick(() => {
  const target = chatContainer.value?.querySelector(`[data-message-id="${CSS.escape(messageId)}"]`) as HTMLElement | null
  if (chatContainer.value && target) {
    chatContainer.value.scrollTop = Math.max(0, target.offsetTop - 16)
  }
})

const useTemplate = (template: string) => {
  // 交付看板模板依赖上一轮方案，若无方案则提示先跑一次配置。
  const needConfigTemplates = [
    '基于上一轮已确认配置，生成 7 阶段装配式交付看板。',
  ]
  if (needConfigTemplates.includes(template) && !latestConfiguration.value) {
    messages.value.push({
      id: Date.now().toString(),
      role: 'agent',
      content: '提示：该模板依赖已确认的配置方案，请先运行一次空间配置 Agent（如模板 01 或 02），再使用本模板。',
      generation_mode: 'frontend_rule_fallback',
    })
    return
  }
  inputMessage.value = template
  handleSend()
}

const handleSend = async () => {
  const content = inputMessage.value.trim()
  if (!content || loading.value) return
  messages.value.push({ id: Date.now().toString(), role: 'user', content })
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()
  try {
    let response: any
    try {
      response = await demoChatWithFastFallback({ message: content, context: { configuration: latestConfiguration.value } })
    } catch {
      console.error('[AIChat] demo-chat fallback triggered')
      const isIntelligenceUpgrade = content.includes('升级') || content.includes('智能化等级')
      const isRiskRequest = content.includes('风险') && (content.includes('吊装') || content.includes('场地') || content.includes('前置确认') || content.includes('道路'))
      const deliveryRequest = !isIntelligenceUpgrade && (content.includes('交付看板') || content.includes('交付阶段') || content.includes('交付风险') || content.includes('生成交付') || content.includes('装配式交付') || isRiskRequest)
      if (deliveryRequest) {
        if (isRiskRequest) {
          response = {
            message: '**LLM 请求超时或失败，已切换为本地规则兜底生成风险评估**',
            agent: 'delivery_planning',
            generation_mode: 'frontend_rule_fallback',
            llm_provider: null,
            generated_delivery: {
              intent: 'risk_assessment',
              project_name: '瑞泽·海度假民宿 38㎡单体扩建（规则型 PoC）',
              real_project_name: '瑞泽·海度假民宿',
              recommended_product: 'Capsule Cabin S',
              recommended_area_sqm: 38,
              generation_mode: 'frontend_rule_fallback',
              site_risks: [
                { category: '运输进场', risk: '滨海场地道路较窄，大型运输车辆转弯半径不足，可能导致到场延误或二次转运。', severity: '高', mitigation: '提前勘察路线，规划临停与调头点，必要时采用小车分批转运。', confirmation_owner: '施工方 + 运输方' },
                { category: '吊装作业', risk: '场地空间有限，吊车支腿展开困难，吊装半径不足影响就位精度。', severity: '高', mitigation: '确认吊车吨位与臂长，必要时采用多机抬吊或调整基础定位。', confirmation_owner: '施工方 + 业主' },
                { category: '防腐防水', risk: '滨海环境下海风盐雾腐蚀、暴雨积水，影响模块连接节点寿命。', severity: '中', mitigation: '连接节点采用不锈钢紧固件，防水涂层升级，接缝处增加排水坡度。', confirmation_owner: '设计方 + 施工方' },
                { category: '供电与网络', risk: '现场供电网络不稳定或容量不足，影响调试和开业。', severity: '中', mitigation: '确认供电容量，预留备用电源，弱电网络提前到货安装。', confirmation_owner: '运营方 + 电气设计' },
              ],
              pre_confirmation_items: [
                '确认道路转弯半径、限高、承载力，规划运输路线与临停方案',
                '确认吊车作业面尺寸、支腿位置与基础间距',
                '确认供电容量与备用电源方案',
                '确认排水、防水、防腐方案已落实',
              ],
            },
            generated_plan: null
          }
        } else {
          const delivery = createRuleBasedDelivery(latestConfiguration.value)
          response = {
            message: '**LLM 请求超时或失败，已切换为本地规则兜底生成交付看板**',
            agent: 'delivery_planning',
            generation_mode: 'frontend_rule_fallback',
            llm_provider: null,
            generated_delivery: {
              ...delivery,
              intent: 'delivery_board',
              generation_mode: 'frontend_rule_fallback'
            },
            generated_plan: null
          }
        }
      } else {
        const plan = isIntelligenceUpgrade && latestConfiguration.value
          ? createIntelligenceUpgradePlan(latestConfiguration.value)
          : createRuleBasedConfiguration(content)
        response = {
          message: isIntelligenceUpgrade
            ? '**LLM 请求超时或失败，已切换为本地规则兜底生成智能化升级方案**'
            : '**LLM 请求超时或失败，已切换为本地规则兜底生成配置方案**',
          agent: 'space_configuration',
          generation_mode: 'frontend_rule_fallback',
          llm_provider: null,
          generated_plan: {
            ...plan,
            generation_mode: 'frontend_rule_fallback'
          },
          generated_delivery: null
        }
      }
    }
    if (response.generated_plan) {
      latestConfiguration.value = response.generated_plan
      saveProjectSnapshot(response.generated_plan)
    }
    if (response.generated_delivery) {
      saveProjectSnapshot(latestConfiguration.value, response.generated_delivery)
    }
    const assistantMessageId = (Date.now() + 1).toString()
    messages.value.push({
      id: assistantMessageId,
      role: 'assistant',
      content: response.message,
      agent: response.agent,
      generation_mode: response.generation_mode,
      llm_provider: response.llm_provider,
      agent_trace: response.generated_plan
        ? buildSpaceAgentTrace(content, response.generated_plan, response.generation_mode, response.llm_provider)
        : response.generated_delivery
          ? buildDeliveryAgentTrace(latestConfiguration.value, response.generated_delivery, response.generation_mode, response.llm_provider)
          : null,
      generated_plan: response.generated_plan,
      generated_delivery: response.generated_delivery
    })
    await scrollToMessage(assistantMessageId)
  } catch (error) {
    Message.error('规则输出失败')
  } finally {
    loading.value = false
  }
}

const generateDelivery = async (configuration: any) => {
  latestConfiguration.value = configuration
  const area = configuration?.recommended_area_sqm || 38
  inputMessage.value = `根据已确认的 ${area}㎡方案生成交付阶段与验收任务。`
  await handleSend()
}

const clearMessages = () => {
  messages.value = []
  latestConfiguration.value = null
}
</script>

<style scoped>
.ai-chat-page {
  min-height: 100vh;
  padding: 38px 56px 0;
  color: #0c1b2a;
  background:
    radial-gradient(circle at 5% 3%, rgba(16, 139, 126, 0.18), transparent 28%),
    radial-gradient(circle at 92% 2%, rgba(244, 130, 166, 0.2), transparent 30%),
    linear-gradient(180deg, #f7fbfa 0%, #edf5f3 42%, #f8f9fb 100%);
}

.page-header {
  max-width: 1848px;
  margin: 0 auto 42px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 28px;
}

.header-copy {
  max-width: 1180px;
}

.header-right {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 18px;
  padding-top: 26px;
}

.header-right :deep(.arco-btn) {
  height: 58px;
  padding: 0 30px;
  border-radius: 999px;
  font-size: 18px;
  font-weight: 900;
  box-shadow: 0 12px 24px rgba(27, 47, 63, 0.14);
}

.back-btn {
  border: 1px solid #e1e7ef;
  background: rgba(255, 255, 255, 0.92);
  color: #43566f;
}

.project-btn {
  min-width: 158px;
}

.eyebrow {
  margin: 0;
  color: #087c72;
  font-size: 17px;
  font-weight: 800;
  letter-spacing: 0;
}

.hero-pill,
.guide-pill {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 9px 19px;
  border: 1px solid rgba(45, 80, 88, 0.12);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 6px 14px rgba(27, 47, 63, 0.12);
}

.hero-pill svg,
.guide-pill svg {
  color: #f482a6;
  font-size: 18px;
}

h1 {
  margin: 22px 0 0;
  font-size: 74px;
  line-height: 1.08;
  font-weight: 950;
  letter-spacing: 0;
}

.page-header p:not(.eyebrow) {
  margin: 18px 0 0;
  color: #607188;
  font-size: 25px;
}

.workspace {
  max-width: 1848px;
  min-height: 886px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 520px minmax(0, 1fr);
  gap: 36px;
}

.templates,
.chat-panel {
  border: 1px solid rgba(31, 45, 61, 0.08);
  border-radius: 36px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 34px 80px rgba(34, 59, 73, 0.12);
  backdrop-filter: blur(14px);
}

.templates {
  position: relative;
  padding: 34px 30px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow: hidden;
}

.templates::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 5px;
  background: linear-gradient(90deg, #087c72, #f482a6);
}

.side-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.side-heading h2 {
  margin: 0;
  font-size: 32px;
  line-height: 1;
  font-weight: 950;
}

.side-heading span {
  color: #087c72;
  font-size: 16px;
  font-weight: 900;
}

.template-card {
  position: relative;
  height: auto;
  min-height: 160px;
  padding: 26px 62px 26px 24px;
  border: 1px solid #e4ebef;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.74);
  color: #41536c;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(26, 45, 62, 0.08);
  text-align: left;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.template-card:hover {
  transform: translateY(-2px);
  border-color: rgba(8, 124, 114, 0.24);
  background: #ffffff;
  box-shadow: 0 18px 34px rgba(26, 45, 62, 0.12);
}

.template-index {
  display: block;
  margin-bottom: 22px;
  color: #087c72;
  font-size: 15px;
  font-weight: 950;
  text-transform: uppercase;
}

.template-text {
  display: block;
  font-size: 21px;
  font-weight: 800;
  line-height: 1.75;
}

.template-arrow {
  position: absolute;
  top: 30px;
  right: 24px;
  color: #c4d2df;
  font-size: 22px;
}

.demo-note {
  margin-top: auto;
  min-height: 254px;
  padding: 30px;
  border: 1px solid rgba(8, 124, 114, 0.14);
  border-radius: 30px;
  background:
    radial-gradient(circle at 18% 16%, rgba(8, 124, 114, 0.1), transparent 36%),
    rgba(246, 253, 250, 0.86);
  color: #33433c;
}

.demo-icon {
  width: 58px;
  height: 58px;
  margin-bottom: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: #087c72;
  color: #fff;
  font-size: 28px;
  box-shadow: 0 12px 22px rgba(8, 124, 114, 0.26);
}

.demo-note strong {
  display: block;
  color: #0c1b2a;
  font-size: 29px;
  font-weight: 950;
}

.demo-note p {
  margin: 20px 0 0;
  color: #40546f;
  line-height: 1.7;
  font-size: 18px;
  font-weight: 600;
}

.chat-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-metrics {
  min-height: 144px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border-bottom: 1px solid #e3ebef;
}

.panel-metrics section {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 28px 44px;
}

.panel-metrics section + section {
  border-left: 1px solid #e3ebef;
}

.metric-icon {
  width: 68px;
  height: 68px;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 24px;
  background: #e8f6f3;
  color: #087c72;
  font-size: 31px;
}

.panel-metrics p {
  margin: 0 0 7px;
  color: #9aacbd;
  font-size: 17px;
  font-weight: 950;
  letter-spacing: 0.06em;
}

.panel-metrics strong {
  color: #26354a;
  font-size: 24px;
  font-weight: 950;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 80px 84px;
  background: linear-gradient(180deg, rgba(246, 253, 250, 0.78), rgba(255, 255, 255, 0.86));
}

.empty-guide {
  position: relative;
  max-width: 1120px;
  margin: 0 auto;
  padding: 50px;
  overflow: hidden;
  border: 1px solid rgba(8, 124, 114, 0.12);
  border-radius: 36px;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0) 0 78%, rgba(244, 130, 166, 0.19) 78% 100%),
    rgba(248, 253, 250, 0.92);
  box-shadow: 0 28px 80px rgba(27, 47, 63, 0.1);
}

.empty-guide::after {
  content: 'AI';
  position: absolute;
  right: 22px;
  bottom: -8px;
  color: rgba(225, 91, 112, 0.11);
  font-size: 126px;
  font-weight: 900;
  line-height: 1;
}

.empty-guide > * {
  position: relative;
  z-index: 1;
}

.empty-guide h2 {
  max-width: 1000px;
  margin: 30px 0 32px;
  font-size: 53px;
  line-height: 1.18;
  font-weight: 950;
}

.agent-flow-strip {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 34px;
  margin: 0 0 40px;
}

.agent-flow-strip span {
  position: relative;
  min-height: 54px;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e1ebef;
  border-radius: 999px;
  background: #ffffff;
  color: #087c72;
  font-size: 17px;
  font-weight: 950;
  text-align: center;
  box-shadow: 0 6px 13px rgba(27, 47, 63, 0.1);
}

.agent-flow-strip span:not(:last-child)::after {
  content: '→';
  position: absolute;
  right: -26px;
  z-index: 2;
  color: #f482a6;
  font-size: 25px;
  font-weight: 700;
}

.empty-guide ol {
  display: grid;
  gap: 16px;
  margin: 0;
  padding: 0;
  list-style: none;
  color: #53657b;
}

.empty-guide li {
  min-height: 76px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #dfe9ee;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.78);
  font-size: 22px;
  font-weight: 650;
}

.empty-guide li svg {
  flex: 0 0 auto;
  color: #087c72;
  font-size: 28px;
}

.empty-guide li b {
  color: #f482a6;
  font-size: 24px;
  font-weight: 950;
}

.guide-note {
  margin: 40px 0 0;
  padding: 28px 30px;
  border: 1px solid #e3ebef;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  color: #087c72;
  font-size: 22px;
  line-height: 1.75;
  font-weight: 700;
  box-shadow: 0 8px 18px rgba(27, 47, 63, 0.08);
}

.message {
  max-width: 980px;
  margin: 0 auto 18px;
}

.message-label {
  margin-bottom: 8px;
  color: #1d6f5c;
  font-size: 13px;
  font-weight: 800;
}

.message.user .message-label {
  color: #9a4d5d;
}

.message-body {
  padding: 15px 17px;
  border: 1px solid rgba(31, 45, 61, 0.06);
  border-radius: 18px;
  background: #f6f8f8;
  line-height: 1.75;
}

.message.user .message-body {
  border-color: rgba(225, 91, 112, 0.14);
  background: #fff6f7;
}

.agent-trace-card {
  margin-top: 12px;
  padding: 18px;
  border: 1px solid rgba(29, 111, 92, 0.2);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(29, 111, 92, 0.09), rgba(255, 255, 255, 0) 46%),
    #fbfefd;
  box-shadow: 0 18px 46px rgba(28, 79, 67, 0.08);
}

.trace-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.trace-head h3 {
  margin: 3px 0 0;
  color: #17202a;
  font-size: 18px;
}

.trace-head > span {
  flex: 0 0 auto;
  padding: 7px 10px;
  border: 1px solid rgba(29, 111, 92, 0.22);
  border-radius: 999px;
  background: #effaf5;
  color: #1d6f5c;
  font-size: 12px;
  font-weight: 800;
}

.trace-kicker {
  margin: 0;
  color: #1d6f5c;
  font-size: 12px;
  font-weight: 900;
}

.trace-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr);
  gap: 12px;
}

.trace-panel {
  padding: 13px;
  border: 1px solid rgba(31, 45, 61, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.86);
}

.trace-panel h4 {
  margin: 0 0 10px;
  color: #203d35;
  font-size: 14px;
}

.trace-panel ul {
  margin: 0;
  padding-left: 18px;
  color: #4e5969;
  line-height: 1.75;
}

.signal-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.signal-list span {
  min-height: 58px;
  padding: 10px;
  border-radius: 16px;
  background: #f2f7f5;
  color: #3f4d5a;
  line-height: 1.45;
  font-size: 13px;
}

.signal-list b {
  display: block;
  margin-bottom: 3px;
  color: #1d6f5c;
  font-size: 12px;
}

.agent-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.agent-steps article {
  min-height: 128px;
  padding: 13px;
  border: 1px solid rgba(31, 45, 61, 0.08);
  border-radius: 18px;
  background: #fff;
}

.agent-steps span {
  display: block;
  margin-bottom: 12px;
  color: #e15b70;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-weight: 900;
}

.agent-steps strong {
  display: block;
  margin-bottom: 6px;
  color: #17202a;
  font-size: 15px;
}

.agent-steps p {
  margin: 0;
  color: #5f6b76;
  font-size: 13px;
  line-height: 1.65;
}

.result-card {
  margin-top: 12px;
  padding: 18px;
  border: 1px solid rgba(31, 45, 61, 0.1);
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 14px 34px rgba(25, 38, 52, 0.06);
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  color: #17202a;
  font-size: 17px;
  font-weight: 900;
}

.llm-insight-card {
  margin: 12px 0 14px;
  padding: 15px;
  border: 1px solid rgba(29, 111, 92, 0.18);
  border-radius: 20px;
  background: linear-gradient(135deg, #f0fbf7, #ffffff);
}

.llm-insight-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.llm-insight-head span {
  color: #1d6f5c;
  font-size: 14px;
  font-weight: 900;
}

.llm-insight-head small {
  color: #6b7785;
  font-size: 12px;
}

.llm-insight-card p {
  margin: 0 0 10px;
  color: #33433c;
  line-height: 1.7;
}

.llm-insight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.llm-insight-grid section {
  padding: 10px;
  border: 1px solid rgba(31, 45, 61, 0.08);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.78);
}

.llm-insight-grid h4 {
  margin: 0 0 6px;
  color: #17202a;
  font-size: 13px;
}

.llm-insight-grid ul {
  margin: 0;
  padding-left: 18px;
  color: #4e5969;
  line-height: 1.65;
  font-size: 13px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0;
}

.result-card h3 {
  margin: 14px 0 8px;
  font-size: 15px;
}

.result-card ul {
  margin: 0;
  padding-left: 18px;
  line-height: 1.8;
}

.budget-note {
  margin: 12px 0 0;
  color: #6b7785;
  font-size: 13px;
}

.phase-list {
  display: grid;
  gap: 10px;
}

.phase-item {
  padding: 13px;
  border: 1px solid rgba(31, 45, 61, 0.07);
  border-radius: 18px;
  background: #f7f8fa;
}

.phase-item h3 {
  margin: 0 0 8px;
}

.phase-item p {
  margin: 6px 0;
  color: #4e5969;
  line-height: 1.6;
}

.upgrade-delta-card {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid rgba(8, 124, 114, 0.18);
  border-radius: 16px;
  background: #f3fbf8;
}

.upgrade-delta-card > p {
  margin: 8px 0 12px;
  color: #33433c;
  line-height: 1.7;
}

.upgrade-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.upgrade-grid section {
  padding: 12px;
  border: 1px solid rgba(31, 45, 61, 0.08);
  border-radius: 12px;
  background: #ffffff;
}

.upgrade-grid h4 {
  margin: 0 0 8px;
  color: #087c72;
  font-size: 13px;
}

.risk-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.risk-item {
  padding: 14px 16px; border-radius: 10px;
  background: #fff; border: 1px solid rgba(31, 45, 61, 0.08);
}
.risk-item.severity-高 { border-left: 4px solid #ef4444; }
.risk-item.severity-中 { border-left: 4px solid #f59e0b; }
.risk-item.severity-低 { border-left: 4px solid #10b981; }
.risk-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.risk-category { font-size: 12px; color: rgba(31, 45, 61, 0.5); }
.risk-severity { font-size: 12px; font-weight: 700; }
.severity-高 .risk-severity { color: #ef4444; }
.severity-中 .risk-severity { color: #f59e0b; }
.severity-低 .risk-severity { color: #10b981; }
.risk-desc { font-size: 14px; color: #111827; margin-bottom: 6px; }
.risk-mitigation, .risk-owner { font-size: 13px; color: rgba(31, 45, 61, 0.65); margin-bottom: 4px; }
.pre-confirm-list { padding: 14px 16px; border-radius: 10px; background: #fef3c7; border: 1px solid #fde68a; }
.pre-confirm-list h3 { font-size: 14px; color: #92400e; margin-bottom: 8px; }
.pre-confirm-list ul { margin: 0; padding-left: 18px; font-size: 13px; color: #78350f; }

.input-area {
  border-top: 1px solid rgba(31, 45, 61, 0.09);
  padding: 30px 32px;
  background: rgba(255, 255, 255, 0.82);
}

.input-area :deep(.arco-textarea-wrapper) {
  border-color: rgba(31, 45, 61, 0.08);
  border-radius: 24px;
  background: #f4f7fb;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 22px;
  margin-top: 22px;
}

.input-actions :deep(.arco-btn) {
  min-width: 154px;
  height: 72px;
  border-radius: 24px;
  font-size: 23px;
  font-weight: 950;
}

:deep(.arco-btn-primary) {
  border-color: #087c72;
  background: linear-gradient(135deg, #087c72, #42b8ad);
  box-shadow: 0 15px 28px rgba(8, 124, 114, 0.28);
}

:deep(.arco-btn-primary:hover) {
  border-color: #06675f;
  background: linear-gradient(135deg, #06675f, #2faaa0);
}

@media (max-width: 1300px) {
  .ai-chat-page {
    padding: 28px 32px 0;
  }

  h1 {
    font-size: 54px;
  }

  .page-header p:not(.eyebrow) {
    font-size: 20px;
  }

  .workspace {
    height: auto;
    grid-template-columns: 1fr;
  }

  .templates {
    min-height: auto;
  }

  .template-card {
    min-height: 118px;
  }

  .chat-panel {
    min-height: 780px;
  }
}

@media (max-width: 760px) {
  .ai-chat-page {
    padding: 16px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
    margin-bottom: 24px;
  }

  .header-right {
    width: 100%;
    align-items: stretch;
    flex-direction: column;
    padding-top: 0;
  }

  h1 {
    font-size: 42px;
  }

  .page-header p:not(.eyebrow) {
    font-size: 18px;
  }

  .workspace {
    gap: 20px;
  }

  .templates,
  .chat-panel {
    border-radius: 8px;
  }

  .templates {
    padding: 22px 20px;
  }

  .template-card {
    min-height: 118px;
    border-radius: 8px;
  }

  .template-text {
    font-size: 16px;
  }

  .panel-metrics {
    grid-template-columns: 1fr;
  }

  .panel-metrics section {
    padding: 18px 22px;
  }

  .panel-metrics section + section {
    border-left: 0;
    border-top: 1px solid #e3ebef;
  }

  .message-list {
    padding: 16px;
  }

  .empty-guide {
    padding: 22px;
    margin: 8px auto;
    border-radius: 8px;
  }

  .empty-guide h2 {
    font-size: 32px;
  }

  .agent-flow-strip,
  .trace-grid,
  .agent-steps,
  .llm-insight-grid,
  .signal-list {
    grid-template-columns: 1fr;
  }

  .agent-flow-strip span:not(:last-child)::after {
    right: auto;
    bottom: -14px;
    transform: rotate(90deg);
  }

  .empty-guide li {
    align-items: flex-start;
    font-size: 16px;
    border-radius: 8px;
  }

  .guide-note {
    font-size: 17px;
    border-radius: 8px;
  }

  .input-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .input-actions :deep(.arco-btn) {
    min-width: 0;
    height: 54px;
    border-radius: 8px;
    font-size: 17px;
  }
}
/* Compact scale: keep the Figma-style UI, restore the previous page density. */
.ai-chat-page {
  padding: 24px !important;
}

.page-header {
  position: relative !important;
  max-width: 1180px !important;
  margin: 0 auto 18px !important;
  padding: 26px 28px !important;
  align-items: flex-end !important;
  gap: 16px !important;
  overflow: hidden !important;
  border: 1px solid rgba(31, 45, 61, 0.08) !important;
  border-radius: 8px !important;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(249, 252, 248, 0.78)),
    linear-gradient(90deg, rgba(23, 32, 42, 0.06), rgba(40, 112, 94, 0.04)) !important;
  box-shadow: 0 24px 70px rgba(25, 38, 52, 0.09) !important;
}

.page-header::before {
  content: '' !important;
  position: absolute !important;
  inset: 0 auto 0 0 !important;
  width: 5px !important;
  background: linear-gradient(180deg, #1d6f5c, #e15b70) !important;
}

.header-copy {
  max-width: 880px !important;
}

.header-right {
  position: relative !important;
  z-index: 1 !important;
  flex-direction: column !important;
  gap: 8px !important;
  padding-top: 0 !important;
}

.header-right :deep(.arco-btn) {
  height: 32px !important;
  padding: 0 14px !important;
  border-radius: 8px !important;
  font-size: 14px !important;
  box-shadow: none !important;
}

.back-btn {
  border: 0 !important;
  background: transparent !important;
}

.hero-pill,
.guide-pill {
  gap: 7px !important;
  padding: 7px 12px !important;
  font-size: 12px !important;
}

.hero-pill svg,
.guide-pill svg {
  font-size: 14px !important;
}

h1 {
  margin-top: 12px !important;
  font-size: 40px !important;
}

.page-header p:not(.eyebrow) {
  margin-top: 12px !important;
  font-size: 15px !important;
}

.workspace {
  max-width: 1180px !important;
  height: calc(100vh - 132px) !important;
  min-height: 660px !important;
  grid-template-columns: 320px minmax(0, 1fr) !important;
  gap: 18px !important;
}

.templates,
.chat-panel {
  border-radius: 8px !important;
  box-shadow: 0 18px 56px rgba(25, 38, 52, 0.08) !important;
}

.templates {
  padding: 18px !important;
  gap: 12px !important;
}

.templates::before {
  height: 3px !important;
}

.side-heading {
  margin-bottom: 4px !important;
}

.side-heading h2 {
  font-size: 18px !important;
}

.side-heading span {
  font-size: 12px !important;
}

.template-card {
  min-height: 76px !important;
  padding: 10px 34px 10px 12px !important;
  border-radius: 8px !important;
}

.template-index {
  margin-bottom: 6px !important;
  font-size: 11px !important;
}

.template-text {
  font-size: 14px !important;
  font-weight: 500 !important;
  line-height: 1.55 !important;
}

.template-arrow {
  top: 14px !important;
  right: 12px !important;
  font-size: 16px !important;
}

.demo-note {
  min-height: auto !important;
  padding: 14px !important;
  border-radius: 8px !important;
}

.demo-icon {
  width: 34px !important;
  height: 34px !important;
  margin-bottom: 10px !important;
  border-radius: 10px !important;
  font-size: 17px !important;
}

.demo-note strong {
  font-size: 15px !important;
}

.demo-note p {
  margin-top: 8px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}

.panel-metrics {
  min-height: 72px !important;
}

.panel-metrics section {
  gap: 12px !important;
  padding: 14px 22px !important;
}

.metric-icon {
  width: 42px !important;
  height: 42px !important;
  border-radius: 14px !important;
  font-size: 20px !important;
}

.panel-metrics p {
  margin-bottom: 3px !important;
  font-size: 11px !important;
}

.panel-metrics strong {
  font-size: 15px !important;
}

.message-list {
  padding: 18px !important;
}

.empty-guide {
  max-width: 720px !important;
  margin: 24px auto !important;
  padding: 24px !important;
  border-radius: 8px !important;
  box-shadow: 0 22px 62px rgba(25, 38, 52, 0.08) !important;
}

.empty-guide h2 {
  max-width: 680px !important;
  margin: 16px 0 18px !important;
  font-size: 26px !important;
}

.agent-flow-strip {
  gap: 8px !important;
  margin-bottom: 18px !important;
}

.agent-flow-strip span {
  min-height: 40px !important;
  padding: 8px 10px !important;
  font-size: 12px !important;
}

.agent-flow-strip span:not(:last-child)::after {
  right: -10px !important;
  font-size: 14px !important;
}

.empty-guide ol {
  gap: 10px !important;
}

.empty-guide li {
  min-height: 42px !important;
  padding: 10px 12px !important;
  gap: 10px !important;
  border-radius: 8px !important;
  font-size: 14px !important;
}

.empty-guide li svg {
  font-size: 17px !important;
}

.empty-guide li b {
  font-size: 15px !important;
}

.guide-note {
  margin-top: 16px !important;
  padding: 14px 16px !important;
  border-radius: 8px !important;
  font-size: 14px !important;
}

.input-area {
  padding: 14px 18px !important;
}

.input-area :deep(.arco-textarea-wrapper) {
  border-radius: 8px !important;
}

.input-actions {
  justify-content: space-between !important;
  gap: 10px !important;
  margin-top: 10px !important;
}

.input-actions :deep(.arco-btn) {
  min-width: 0 !important;
  height: 32px !important;
  border-radius: 6px !important;
  font-size: 14px !important;
}

@media (max-width: 1300px) {
  .workspace {
    height: auto !important;
    grid-template-columns: 1fr !important;
  }
}
</style>
