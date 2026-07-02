<template>
  <main class="projects-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">规则型 PoC 项目</p>
        <h1>民宿配置项目列表</h1>
      </div>
      <a-button type="primary" @click="$router.push('/chat')">创建配置方案</a-button>
    </header>

    <a-card class="project-card" hoverable @click="$router.push('/project/demo-capsule-cabin')">
      <div class="project-row">
        <img src="/assets/capsule_cabin/人视图.png" alt="瑞泽·海度假民宿案例" />
        <div class="project-info">
          <a-tag color="green">项目复盘规则</a-tag>
          <h2>瑞泽·海度假民宿 38㎡单体扩建（规则型 PoC）</h2>
          <p>Capsule Cabin S / 最多 4 人入住 / 偏无人化运营 + 基础智能控制</p>
          <div class="meta">
            <span>空间配置 Agent</span>
            <span>交付规划 Agent</span>
            <span>示例预算区间，非正式报价</span>
          </div>
        </div>
        <a-button>查看</a-button>
      </div>
    </a-card>
  </main>
</template>

<style scoped>
.projects-page { min-height: 100vh; background: #f6f7f8; padding: 32px 24px; color: #1d2129; }
.page-header { max-width: 1040px; margin: 0 auto 20px; display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.eyebrow { margin: 0 0 6px; color: #28705e; font-size: 13px; font-weight: 700; }
h1 { margin: 0; font-size: 30px; }
.project-card { max-width: 1040px; margin: 0 auto; border-radius: 8px; cursor: pointer; }
.project-row { display: grid; grid-template-columns: 220px 1fr auto; gap: 22px; align-items: center; }
.project-row img { width: 220px; height: 132px; object-fit: cover; border-radius: 6px; background: #eef2ef; }
.project-info h2 { margin: 10px 0 8px; font-size: 22px; }
.project-info p { margin: 0; color: #5f6b76; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.meta span { padding: 5px 9px; background: #eef2f5; border-radius: 6px; color: #4e5969; font-size: 13px; }
@media (max-width: 760px) {
  .page-header, .project-row { align-items: flex-start; grid-template-columns: 1fr; flex-direction: column; }
  .project-row img { width: 100%; height: auto; aspect-ratio: 16 / 9; }
}
</style>
