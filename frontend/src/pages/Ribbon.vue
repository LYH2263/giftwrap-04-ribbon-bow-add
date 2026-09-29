<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
import CompareBoard from '../components/CompareBoard.vue'

const boxes = ref([])
const bid = ref(1)
const defaultBow = ref(0.3)
const savedAt = ref('')
const err = ref('')
const out = ref(null)

async function dry() {
  err.value = ''
  try {
    out.value = await getJSON(
      `/api/estimate?box_id=${bid.value}&bow_enabled=true&bow_m=${Number(defaultBow.value)}`,
    )
  } catch (e) {
    err.value = String(e.message || e)
  }
}

onMounted(async () => {
  try {
    const [bs, settings] = await Promise.all([getJSON('/api/boxes'), getJSON('/api/settings')])
    boxes.value = bs.items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    defaultBow.value = Number(settings.bow_m ?? 0.3)
    await dry()
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function saveDefault() {
  err.value = ''
  if (!(Number(defaultBow.value) > 0)) {
    err.value = '默认结长须大于 0。'
    return
  }
  try {
    const s = await putJSON('/api/settings', { bow_m: Number(defaultBow.value) })
    defaultBow.value = Number(s.bow_m)
    savedAt.value = '已保存'
    setTimeout(() => (savedAt.value = ''), 2000)
    await dry()
  } catch (e) {
    err.value = String(e.message || e)
  }
}
</script>

<template>
  <div class="page">
    <h1>丝带</h1>
    <p class="lede">
      十字捆扎长度跟盒体三边走；打蝴蝶结时最终丝带＝捆扎米数＋结长。结长只加丝带，不影响用纸面积。
    </p>

    <div class="row">
      <label class="field">
        默认结长
        <input v-model.number="defaultBow" min="0.01" step="0.05" type="number" />
        m
      </label>
      <button :disabled="!(Number(defaultBow) > 0)" @click="saveDefault">保存默认结长</button>
      <span class="saved">{{ savedAt }}</span>
    </div>
    <p class="stat-line">改默认结长只影响今后的新算单；已经写入用纸档的 ribbon_m 钉住写入值，不重算。</p>

    <p v-if="err" class="bad">{{ err }}</p>

    <div class="result-board">
      <div class="row">
        <select v-model.number="bid" @change="dry">
          <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
        <span class="pill">打蝴蝶结 · 用当前默认结长试算</span>
      </div>
      <CompareBoard
        v-if="out"
        :base-m="out.ribbon.base_m"
        :bow-enabled="out.ribbon.bow_enabled"
        :bow-m="out.ribbon.bow_m"
        :paper-m2="out.paper_m2"
        :ribbon-m="out.ribbon.ribbon_m"
      />
    </div>
  </div>
</template>

<style scoped>
.field {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
}
.field input {
  width: 100px;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.72);
  font: inherit;
}
.saved {
  color: var(--ok);
  font-weight: 600;
  font-size: 0.9rem;
}
</style>
