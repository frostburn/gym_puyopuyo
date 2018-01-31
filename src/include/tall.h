#ifndef GYM_PUYOPUYO_TALL_H_GUARD
#define GYM_PUYOPUYO_TALL_H_GUARD

#define NUM_FLOORS (2)

#define LIFE_BLOCK (0xFFFFFFFF00000000ULL)
#define SEMI_LIFE_BLOCK (0xFFFFFFFFFF000000ULL)

// Classic scoring
#define MAX_GROUP_BONUS (7)
#define MAX_COLOR_BONUS (7)
#define MAX_CHAIN_POWER (23)
#define MAX_CLEAR_BONUS (999)

extern const int COLOR_BONUS[];
extern const int GROUP_BONUS[];
extern const int CHAIN_POWERS[];

void tall_render(puyos_t *floors, int num_colors);

int tall_handle_gravity(puyos_t *floors, int num_colors);

int tall_clear_groups(puyos_t *bottom, puyos_t *top, int num_colors, int chain_number, int tsu_rules, puyos_t *cleared);

int tall_resolve(puyos_t *floors, int num_colors, int tsu_rules, int has_garbage, int *chain_out);

int tall_clear_groups_and_garbage(puyos_t *floors, int num_layers, int chain_number, int tsu_rules, int has_garbage);

char* tall_encode(puyos_t *floors, int num_colors);

bitset_t tall_valid_moves(puyos_t *floors, int num_colors, int width, int tsu_rules);

double tall_tree_search(puyos_t*, int, int, int, int, bitset_t, int*, int, int, double, puyos_t*);

#endif /* !GYM_PUYOPUYO_TALL_H_GUARD */
