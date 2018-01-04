#include <Python.h>

#include "include/bitboard.h"
#include "include/bottom.h"
#include "include/tall.h"

static PyObject *
py_bottom_render(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yi", &data, &num_colors))
  {
    return NULL;
  }
  bottom_render(data->ob_start, num_colors);

  Py_RETURN_NONE;
}

static PyObject *
py_bottom_handle_gravity(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yi", &data, &num_colors))
  {
    return NULL;
  }
  int iterations = bottom_handle_gravity(data->ob_start, num_colors);

  return Py_BuildValue("i", iterations);
}

static PyObject *
py_bottom_resolve(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yi", &data, &num_colors))
  {
    return NULL;
  }
  int chain = bottom_resolve(data->ob_start, num_colors);

  return Py_BuildValue("i", chain);
}

static PyObject *
py_bottom_encode(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yi", &data, &num_colors))
  {
    return NULL;
  }
  char *encoded = bottom_encode(data->ob_start, num_colors);

  PyObject *result = Py_BuildValue("y#", encoded, num_colors * WIDTH * HEIGHT);
  free(encoded);
  return result;
}

static PyObject *
py_bottom_valid_moves(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yi", &data, &num_colors))
  {
    return NULL;
  }
  bitset_t valid = bottom_valid_moves(data->ob_start, num_colors);

  return Py_BuildValue("K", valid);
}

static PyObject *
py_tall_render(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yi", &data, &num_colors))
  {
    return NULL;
  }
  tall_render(data->ob_start, num_colors);

  Py_RETURN_NONE;
}

static PyObject *
py_tall_handle_gravity(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yi", &data, &num_colors))
  {
    return NULL;
  }
  int iterations = tall_handle_gravity(data->ob_start, num_colors);

  return Py_BuildValue("i", iterations);
}

static PyObject *
py_tall_resolve(PyObject *self, PyObject *args)
{
  int num_colors;
  int tsu_rules;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Yip", &data, &num_colors, &tsu_rules))
  {
    return NULL;
  }
  int chain;
  int score = tall_resolve(data->ob_start, num_colors, tsu_rules, &chain);

  return Py_BuildValue("ii", score, chain);
}

static PyMethodDef PuyoMethods[] = {
  {"bottom_render", py_bottom_render, METH_VARARGS, "Debug print for bottom state inspection."},
  {"bottom_handle_gravity", py_bottom_handle_gravity, METH_VARARGS, "Handle puyo gravity for a bottom state."},
  {"bottom_resolve", py_bottom_resolve, METH_VARARGS, "Fully resolve a bottom state and return the chain length."},
  {"bottom_encode", py_bottom_encode, METH_VARARGS, "Encodes a bottom state as an array of chars."},
  {"bottom_valid_moves", py_bottom_valid_moves, METH_VARARGS, "Returns a bitset of valid moves on a bottom state."},
  {"tall_render", py_tall_render, METH_VARARGS, "Debug print for tall state inspection."},
  {"tall_handle_gravity", py_tall_handle_gravity, METH_VARARGS, "Handle puyo gravity for a tall state."},
  {"tall_resolve", py_tall_resolve, METH_VARARGS, "Fully resolve a tall state and return the score and the chain length."},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef puyomodule = {
  PyModuleDef_HEAD_INIT,
  "puyocore",  /* name of module */
  "In-place core methods for Puyo Puyo states",  /* module documentation, may be NULL */
  -1,  /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
  PuyoMethods
};
PyMODINIT_FUNC
PyInit_puyocore(void)
{
  PyObject *m;

  m = PyModule_Create(&puyomodule);
  if (m == NULL) {
    return NULL;
  }

  return m;
}