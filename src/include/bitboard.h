#ifndef GYM_PUYOPUYO_BITBOARD_H_GUARD
#define GYM_PUYOPUYO_BITBOARD_H_GUARD

#define WIDTH (8)
#define HEIGHT (8)
#define CLEAR_THRESHOLD (4)
#define H_SHIFT (1)
#define V_SHIFT (WIDTH)
#define TOP_TO_BOTTOM (V_SHIFT * (HEIGHT - 1))
#define TOP (0xFFULL)
#define BOTTOM (0xFF00000000000000ULL)
#define RIGHT_BLOCK (0xFEFEFEFEFEFEFEFEULL)
#define FULL (0xFFFFFFFFFFFFFFFFULL)
#define NUM_ACTIONS (4 * WIDTH - 2)

typedef unsigned long long puyos_t;
typedef unsigned long long bitset_t;

int popcount(puyos_t puyos);

puyos_t cross(puyos_t puyos);

puyos_t flood(register puyos_t source, register puyos_t target);

int popcount_2(puyos_t *puyos);

void flood_2(puyos_t *source, puyos_t *target);

void cross_2(puyos_t *puyos);

#endif /* !GYM_PUYOPUYO_BITBOARD_H_GUARD */
