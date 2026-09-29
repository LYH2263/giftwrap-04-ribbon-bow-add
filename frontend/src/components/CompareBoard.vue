<script setup>
defineProps({
  paperM2: { type: [Number, String], default: null },
  ribbonM: { type: [Number, String], default: null },
  bowEnabled: { type: Boolean, default: false },
  bowM: { type: [Number, String], default: 0 },
  baseM: { type: [Number, String], default: null },
  pinned: { type: Boolean, default: false },
})
</script>

<template>
  <div class="compare">
    <div class="compare-cell paper">
      <span class="compare-label">用纸面积</span>
      <span class="compare-value">{{ paperM2 ?? '—' }}<em>m²</em></span>
      <span class="compare-note">不含结长，不随结长变化</span>
    </div>
    <div class="compare-vs">对照</div>
    <div class="compare-cell ribbon">
      <span class="compare-label">丝带长度</span>
      <span class="compare-value">{{ ribbonM ?? '—' }}<em>m</em></span>
      <span class="compare-note">
        <template v-if="pinned">已钉住写入值</template>
        <template v-else-if="bowEnabled">捆扎 {{ baseM }} m ＋ 结长 {{ bowM }} m</template>
        <template v-else>纯捆扎，未打结</template>
      </span>
    </div>
  </div>
</template>

<style scoped>
.compare {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: stretch;
  gap: 0.75rem;
  margin: 1rem 0;
}
.compare-cell {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 1rem 1.15rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.85), rgba(228, 239, 232, 0.6));
}
.compare-cell.ribbon {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(243, 197, 207, 0.35));
  border-color: rgba(214, 75, 106, 0.3);
}
.compare-label {
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-soft);
}
.compare-value {
  font-family: var(--font-display);
  font-size: 2.1rem;
  font-weight: 700;
  line-height: 1.05;
  color: var(--wash-b);
  font-variant-numeric: tabular-nums;
}
.compare-cell.ribbon .compare-value {
  color: var(--ribbon);
}
.compare-value em {
  font-style: normal;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--ink-soft);
  margin-left: 0.25rem;
}
.compare-note {
  font-size: 0.82rem;
  color: var(--ink-soft);
}
.compare-vs {
  align-self: center;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: var(--foil);
  font-weight: 700;
}
@media (max-width: 640px) {
  .compare {
    grid-template-columns: 1fr;
  }
  .compare-vs {
    display: none;
  }
}
</style>
