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
