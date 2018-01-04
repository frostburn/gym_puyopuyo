#include "include/bitboard.h"

int popcount(puyos_t puyos) {
  return __builtin_popcountll(puyos);
}

puyos_t flood(register puyos_t source, register puyos_t target) {
  source &= target;
  if (!source){
    return source;
  }
  register puyos_t temp;
  do {
    temp = source;
    source |= (
      ((source & RIGHT_BLOCK) >> H_SHIFT) |
      ((source << H_SHIFT) & RIGHT_BLOCK) |
      (source << V_SHIFT) |
      (source >> V_SHIFT)
    ) & target;
  } while (temp != source);
  return source;
}

int popcount_2(puyos_t *puyos) {
    return __builtin_popcountll(puyos[0]) + __builtin_popcountll(puyos[1]);
}

void flood_2(puyos_t *source, puyos_t *target) {
    source[0] &= target[0];
    source[1] &= target[1];

    if (!(source[0] || source[1])) {
        return;
    }
    puyos_t temp[2];
    do {
        temp[0] = source[0];
        temp[1] = source[1];

        source[0] |= (
            ((source[0] & RIGHT_BLOCK) >> H_SHIFT) |
            ((source[0] << H_SHIFT) & RIGHT_BLOCK) |
            (source[0] << V_SHIFT) |
            (source[0] >> V_SHIFT) |
            ((source[1] & TOP) << TOP_TO_BOTTOM)
        ) & target[0];

        source[1] |= (
            ((source[1] & RIGHT_BLOCK) >> H_SHIFT) |
            ((source[1] << H_SHIFT) & RIGHT_BLOCK) |
            (source[1] << V_SHIFT) |
            (source[1] >> V_SHIFT) |
            ((source[0] & BOTTOM) >> TOP_TO_BOTTOM)
        ) & target[1];
    } while (temp[0] != source[0] || temp[1] != source[1]);
}
