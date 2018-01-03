#ifndef GYM_PUYOPUYO_BITBOARD_H_GUARD
#define GYM_PUYOPUYO_BITBOARD_H_GUARD

#define WIDTH (8)
#define CLEAR_THRESHOLD (4)
#define H_SHIFT (1)
#define V_SHIFT (WIDTH)
#define BOTTOM (0xFF00000000000000ULL)
#define RIGHT_BLOCK (0xFEFEFEFEFEFEFEFEUL)

typedef unsigned long long puyos_t;
typedef unsigned long long bitset_t;

int popcount(puyos_t puyos);

puyos_t flood(register puyos_t source, register puyos_t target);

#endif /* !GYM_PUYOPUYO_BITBOARD_H_GUARD */
