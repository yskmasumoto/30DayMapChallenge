<script setup lang="ts">
import type { TrainLog } from '../types';

defineProps<{
  log: TrainLog;
  isSelected: boolean;
}>();

const emit = defineEmits<{
  (e: 'click', id: string): void;
}>();
</script>

<template>
  <div
    @click="emit('click', log.uniqueId!)"
    class="p-4 mb-3 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md"
    :class="[
      isSelected
        ? 'border-blue-500 bg-blue-50'
        : 'border-gray-200 bg-white hover:border-blue-300'
    ]"
  >
    <div class="flex justify-between items-start mb-2">
      <span class="bg-gray-800 text-white text-xs px-2 py-1 rounded">
        {{ log.company }}
      </span>
      <span class="text-sm text-gray-500">{{ log.departure_day }}</span>
    </div>

    <h3 class="font-bold text-lg text-gray-800 mb-1">
      {{ log.name || log.line }}
      <span v-if="log.serial" class="text-sm font-normal text-gray-500">
        (#{{ log.serial }})
      </span>
    </h3>

    <div class="flex items-center text-sm text-gray-700">
      <div class="flex-1">
        <div class="font-semibold">{{ log.departure_station }}</div>
        <div class="text-xs text-gray-500">{{ log.departure_date || '--:--' }}</div>
      </div>
      <div class="px-2 text-gray-400">➝</div>
      <div class="flex-1 text-right">
        <div class="font-semibold">{{ log.arrival_station }}</div>
        <div class="text-xs text-gray-500">{{ log.arrival_date || '--:--' }}</div>
      </div>
    </div>
  </div>
</template>
