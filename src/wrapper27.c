#include <Python.h>

#include "include/core.h"

static PyObject *
py_bottom_render(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  bottom_render(data->ob_bytes, num_colors);

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
  int iterations = bottom_handle_gravity(data->ob_bytes, num_colors);

  return Py_BuildValue("i", iterations);
}

static PyObject *
py_bottom_resolve(PyObject *self, PyObject *args)
{
  int num_colors;
  const PyByteArrayObject *data;

  if (!PyArg_ParseTuple(args, "Oi", &data, &num_colors))
  {
    return NULL;
  }
  int chain = bottom_resolve(data->ob_bytes, num_colors);

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
  char *encoded = bottom_encode(data->ob_bytes, num_colors);

  PyObject *result = Py_BuildValue("z#", encoded, num_colors * WIDTH * BOTTOM_HEIGHT);
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
  bitset_t valid = bottom_valid_moves(data->ob_bytes, num_colors);

  return Py_BuildValue("K", valid);
}

static PyMethodDef PuyoMethods[] = {
    {"bottom_render", py_bottom_render, METH_VARARGS, "Debug print for bottom state inspection."},
    {"bottom_handle_gravity", py_bottom_handle_gravity, METH_VARARGS, "Handle puyo gravity for a bottom state."},
    {"bottom_resolve", py_bottom_resolve, METH_VARARGS, "Fully resolve a bottom state and return the chain length."},
    {"bottom_encode", py_bottom_encode, METH_VARARGS, "Encodes a bottom state as an array of chars."},
    {"bottom_valid_moves", py_bottom_valid_moves, METH_VARARGS, "Returns a bitset of valid moves on a bottom state."},
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
