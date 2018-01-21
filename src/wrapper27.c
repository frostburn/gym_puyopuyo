#include <Python.h>

#include "bitboard.h"
#include "bottom.h"
#include "tall.h"

static PyObject *
py_bottom_render(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  bottom_render((puyos_t*)data->ob_bytes, num_colors);

  Py_RETURN_NONE;
}

static PyObject *
py_bottom_handle_gravity(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  int iterations = bottom_handle_gravity((puyos_t*)data->ob_bytes, num_colors);

  return Py_BuildValue("i", iterations);
}

static PyObject *
py_bottom_resolve(PyObject *self, PyObject *args)
{
  int num_colors;
  int has_garbage;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oii", &data, &num_colors, &has_garbage))
  {
    return NULL;
  }
  int chain = bottom_resolve((puyos_t*)data->ob_bytes, num_colors, !!has_garbage);

  return Py_BuildValue("i", chain);
}

static PyObject *
py_bottom_encode(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  char *encoded = bottom_encode((puyos_t*)data->ob_bytes, num_colors);

  PyObject *result = Py_BuildValue("z#", encoded, num_colors * WIDTH * HEIGHT);
  free(encoded);
  return result;
}

static PyObject *
py_bottom_valid_moves(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  bitset_t valid = bottom_valid_moves((puyos_t*)data->ob_bytes, num_colors);

  return Py_BuildValue("K", valid);
}

static PyObject *
py_bottom_tree_search(PyObject *self, PyObject *args)
{
  const PyByteArrayObject *data;
  int num_layers;
  int has_garbage;
  bitset_t action_mask;
  PyObject *colors_list;
  int depth;
  double factor;

  if (!PyArg_ParseTuple(args, "OiiKOid", &data, &num_layers, &has_garbage, &action_mask, &colors_list, &depth, &factor))
  {
    return NULL;
  }

  int len_colors = PyList_Size(colors_list);
  int *colors;
  if (2 * depth > len_colors) {
    colors = malloc(sizeof(int) * 2 * depth);
  } else {
    colors = malloc(sizeof(int) * len_colors);
  }
  for (int i = 0; i < len_colors; ++i) {
    PyObject *item = PyList_GetItem(colors_list, i);
    if (!item) {
      return NULL;
    }
    int color = PyLong_AsLong(item);
    if (color < 0) {
      return NULL;
    }
    colors[i] = color;
  }

  puyos_t *child_buffer = malloc(sizeof(puyos_t) * num_layers * depth);

  double score = bottom_tree_search((puyos_t*)data->ob_bytes, num_layers, !!has_garbage, action_mask, colors, len_colors / 2, depth, factor, child_buffer);

  free(colors);
  free(child_buffer);

  return Py_BuildValue("d", score);
}

static PyObject *
py_tall_render(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  tall_render((puyos_t*)data->ob_bytes, num_colors);

  Py_RETURN_NONE;
}

static PyObject *
py_tall_handle_gravity(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  int iterations = tall_handle_gravity((puyos_t*)data->ob_bytes, num_colors);

  return Py_BuildValue("i", iterations);
}

static PyObject *
py_tall_resolve(PyObject *self, PyObject *args)
{
  int num_colors;
  int tsu_rules;
  int has_garbage;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oiii", &data, &num_colors, &tsu_rules, &has_garbage))
  {
    return NULL;
  }

  int chain;
  int score = tall_resolve((puyos_t*)data->ob_bytes, num_colors, tsu_rules, !!has_garbage, &chain);

  return Py_BuildValue("ii", score, chain);
}

static PyObject *
py_tall_encode(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  char *encoded = tall_encode((puyos_t*)data->ob_bytes, num_colors);

  PyObject *result = Py_BuildValue("z#", encoded, num_colors * NUM_FLOORS * WIDTH * HEIGHT);
  free(encoded);
  return result;
}

static PyObject *
py_tall_valid_moves(PyObject *self, PyObject *args)
{
  int num_colors;
  int width;
  int tsu_rules;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oiii", &data, &num_colors, &width, &tsu_rules))
  {
    return NULL;
  }
  bitset_t valid = tall_valid_moves((puyos_t*)data->ob_bytes, num_colors, width, tsu_rules);

  return Py_BuildValue("K", valid);
}

static PyObject *
py_tall_tree_search(PyObject *self, PyObject *args)
{
  const PyByteArrayObject *data;
  int num_layers;
  int width;
  int tsu_rules;
  int has_garbage;
  bitset_t action_mask;
  PyObject *colors_list;
  int depth;
  double factor;

  if (!PyArg_ParseTuple(args, "OiiiiKOid", &data, &num_layers, &width, &tsu_rules, &has_garbage, &action_mask, &colors_list, &depth, &factor))
  {
    return NULL;
  }

  int len_colors = PyList_Size(colors_list);
  if (len_colors % 2) {
    return NULL;
  }
  int *colors;
  if (2 * depth > len_colors) {
    colors = malloc(sizeof(int) * 2 * depth);
  } else {
    colors = malloc(sizeof(int) * len_colors);
  }
  for (int i = 0; i < len_colors; ++i) {
    PyObject *item = PyList_GetItem(colors_list, i);
    if (!item) {
      return NULL;
    }
    int color = PyLong_AsLong(item);
    if (color < 0) {
      return NULL;
    }
    colors[i] = color;
  }

  puyos_t *child_buffer = malloc(sizeof(puyos_t) * num_layers * NUM_FLOORS * depth);

  double score = tall_tree_search((puyos_t*)data->ob_bytes, num_layers, width, tsu_rules, has_garbage, action_mask, colors, len_colors / 2, depth, factor, child_buffer);

  free(colors);
  free(child_buffer);

  return Py_BuildValue("d", score);
}

static PyObject *
py_make_move(PyObject *self, PyObject *args)
{
  int action, color_a, color_b;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oiii", &data, &action, &color_a, &color_b))
  {
    return NULL;
  }
  make_move((puyos_t*)data->ob_bytes, action, color_a, color_b);

  Py_RETURN_NONE;
}

static PyObject *
py_mirror(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  mirror((puyos_t*)data->ob_bytes, num_colors);

  Py_RETURN_NONE;
}


static PyMethodDef PuyoMethods[] = {
  {"bottom_render", py_bottom_render, METH_VARARGS, "Debug print for bottom state inspection."},
  {"bottom_handle_gravity", py_bottom_handle_gravity, METH_VARARGS, "Handle puyo gravity for a bottom state."},
  {"bottom_resolve", py_bottom_resolve, METH_VARARGS, "Fully resolve a bottom state and return the chain length."},
  {"bottom_encode", py_bottom_encode, METH_VARARGS, "Encodes a bottom state as an array of chars."},
  {"bottom_valid_moves", py_bottom_valid_moves, METH_VARARGS, "Returns a bitset of valid moves on a bottom state."},
  {"bottom_tree_search", py_bottom_tree_search, METH_VARARGS, "Does a tree search with the given colors."},
  {"tall_render", py_tall_render, METH_VARARGS, "Debug print for tall state inspection."},
  {"tall_handle_gravity", py_tall_handle_gravity, METH_VARARGS, "Handle puyo gravity for a tall state."},
  {"tall_resolve", py_tall_resolve, METH_VARARGS, "Fully resolve a tall state and return the score and the chain length."},
  {"tall_encode", py_tall_encode, METH_VARARGS, "Encodes a tall state as an array of chars."},
  {"tall_valid_moves", py_tall_valid_moves, METH_VARARGS, "Returns a bitset of valid moves on a tall state."},
  {"tall_tree_search", py_tall_tree_search, METH_VARARGS, "Does a tree search with the given colors."},
  {"make_move", py_make_move, METH_VARARGS, "Overlays two puyos of the given colors on top of the field."},
  {"mirror", py_mirror, METH_VARARGS, "Flip the field horizontally."},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initpuyocore(void)
{
    PyObject *m;

    m = Py_InitModule("puyocore", PuyoMethods);
    if (m == NULL) {
        return;
      }
}
