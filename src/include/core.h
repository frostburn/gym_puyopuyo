#define WIDTH (8)
#define BOTTOM_HEIGHT (8)
#define CLEAR_THRESHOLD (4)
#define H_SHIFT (1)
#define V_SHIFT (WIDTH)
#define BOTTOM (0xFF00000000000000ULL)
#define RIGHT_BLOCK (0xFEFEFEFEFEFEFEFEUL)

typedef unsigned long long puyos_t;

int popcount(puyos_t puyos);

puyos_t flood(register puyos_t source, register puyos_t target);

void bottom_render(puyos_t *floor, int num_colors);

int bottom_handle_gravity(puyos_t *floor, int num_colors);

int bottom_clear_groups(puyos_t *floor, int num_colors);

int bottom_resolve(puyos_t *floor, int num_colors);

char* bottom_encode(puyos_t *floor, int num_colors);
