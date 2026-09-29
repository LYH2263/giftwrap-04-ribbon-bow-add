<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'
import CompareBoard from '../components/CompareBoard.vue'

const boxes = ref([])
const bid = ref(1)
const bowEnabled = ref(false)
const bowM = ref(0.3)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    const [bs, settings] = await Promise.all([getJSON('/api/boxes'), getJSON('/api/settings')])
    boxes.value = bs.items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    bowM.value = Number(settings.bow_m ?? 0.3)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function payload() {
  return {
    box_id: bid.value,
    wrap_style: 'cross',
    bow_enabled: bowEnabled.value,
    bow_m: bowEnabled.value ? Number(bowM.value) : null,
  }
}

async function go(save) {
  err.value = ''
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', { ...payload(), save: true })
      : await getJSON(
          `/api/estimate?box_id=${bid.value}&bow_enabled=${bowEnabled.value}` +
            (bowEnabled.value ? `&bow_m=${Number(bowM.value)}` : ''),
        )
  } catch (e) {
    out.value = null
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与丝带，确认后再写入用纸档。打结只加长丝带，纸面积不动。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <label class="bow-toggle">
        <input v-model="bowEnabled" type="checkbox" />
        打蝴蝶结
      </label>
      <label v-if="bowEnabled" class="bow-input">
        结长
        <input v-model.number="bowM" min="0.01" step="0.05" type="number" />
        m
      </label>
    </div>
    <div class="row">
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-if="bowEnabled && !(Number(bowM) > 0)" class="bad">结长须大于 0，否则写入/试算会失败且不入档。</p>
    <div v-if="out" class="result-board">
      <CompareBoard
        :base-m="out.ribbon.base_m"
        :bow-enabled="out.ribbon.bow_enabled"
        :bow-m="out.ribbon.bow_m"
        :paper-m2="out.paper_m2"
        :ribbon-m="out.ribbon.ribbon_m"
      />
      <p v-if="out.run_id" class="stat-line">已写入用纸档 #{{ out.run_id }}，回看以落库值为准。</p>
      <BoxUnfold
        :h="out.box.height"
        :l="out.box.length"
        :paper-m2="out.paper_m2"
        :w="out.box.width"
      />
    </div>
  </div>
</template>

<style scoped>
.bow-toggle,
.bow-input {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  color: var(--ink);
}
.bow-input input {
  width: 96px;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.72);
  font: inherit;
}
.bow-toggle input {
  width: 18px;
  height: 18px;
  accent-color: var(--ribbon);
}
</style>
