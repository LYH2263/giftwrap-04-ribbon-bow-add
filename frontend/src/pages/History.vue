<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import CompareBoard from '../components/CompareBoard.vue'

const items = ref([])
const detail = ref(null)
const err = ref('')
const loading = ref(false)

async function open(r) {
  loading.value = true
  err.value = ''
  try {
    // 详情同样取自落库，不按当前默认结长重算
    detail.value = await getJSON(`/api/runs/${r.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库结果。ribbon_m 与纸面积以写入时为准，之后改默认结长不回算。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <a href="#" @click.prevent="open(r)">
          #{{ r.id }} {{ r.box_name }}
          <span v-if="r.result?.bow_enabled" class="pill bow">蝴蝶结 {{ r.result.bow_m }} m</span>
        </a>
        <span class="meta">
          {{ r.result?.paper_m2 ?? '—' }} m² · 丝带 {{ r.result?.ribbon_m ?? r.result?.ribbon?.ribbon_m ?? '—' }} m
        </span>
      </li>
    </ul>

    <div v-if="detail" class="detail result-board">
      <div class="row" style="justify-content: space-between">
        <strong>#{{ detail.id }} {{ detail.box_name }}</strong>
        <button class="ghost" @click="detail = null">关闭</button>
      </div>
      <CompareBoard
        :base-m="detail.result.ribbon?.base_m ?? null"
        :bow-enabled="!!detail.result.bow_enabled"
        :bow-m="detail.result.bow_m ?? 0"
        :paper-m2="detail.result.paper_m2"
        :pinned="true"
        :ribbon-m="detail.result.ribbon_m ?? detail.result.ribbon?.ribbon_m"
      />
      <p class="stat-line">
        overlap × {{ detail.overlap }} ；wrap_style {{ detail.result.ribbon?.wrap_style ?? '—' }}；以上数值直接读落库。
      </p>
      <p v-if="detail.note" class="meta">备注：{{ detail.note }}</p>
      <p v-if="loading" class="meta">读取中…</p>
    </div>
  </div>
</template>

<style scoped>
.pill.bow {
  margin-left: 0.5rem;
  background: rgba(214, 75, 106, 0.12);
  color: var(--ribbon);
}
.detail {
  padding: 1.15rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.55);
}
</style>
