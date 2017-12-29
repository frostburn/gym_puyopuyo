#include <Python.h>

#define WIDTH (8)
#define BOTTOM_HEIGHT (8)
#define V_SHIFT (WIDTH)
#define BOTTOM (0xFF00000000000000ULL)

typedef unsigned long long puyos_t;


void bottom_render(puyos_t *floor, int num_colors) {
  puyos_t p = 1;
  for (int i = 0; i < BOTTOM_HEIGHT; ++i) {
    for (int j = 0; j < WIDTH; ++j) {
      int empty = 1;
      for (int k = 0; k < num_colors; ++k) {
        if (floor[k] & p) {
          printf("%d ", k);
          empty = 0;
        }
      }
      if (empty) {
        printf(". ");
      }
      p <<= 1;
    }
    printf("\n");
  }
}

int bottom_handle_gravity(puyos_t *floor, int num_colors) {
  puyos_t all;
  all = 0;
  for (int j = 0; j < num_colors; ++j) {
    all |= floor[j];
  }

  int iterations = 0;
  puyos_t temp;
  do {
    temp = all;
    puyos_t bellow, falling;
    bellow = (all >> V_SHIFT) | BOTTOM;
    all = 0;
    for (int i = 0; i < num_colors; ++i) {
      falling = floor[i] & ~bellow;
      floor[i] = (falling << V_SHIFT) | (floor[i] & bellow);
      all |= floor[i];
    }
    ++iterations;
  } while (temp != all);

  return iterations;
}

# if (PY_MAJOR_VERSION == 2)
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
    bottom_handle_gravity(data->ob_bytes, num_colors);

    Py_RETURN_NONE;
  }
#else
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
    bottom_handle_gravity(data->ob_start, num_colors);

    Py_RETURN_NONE;
  }
#endif

static PyMethodDef PuyoMethods[] = {
    {"bottom_render", py_bottom_render, METH_VARARGS, "Debug print for bottom state inspection."},
    {"bottom_handle_gravity", py_bottom_handle_gravity, METH_VARARGS, "Handle puyo gravity for a bottom state."},
    {NULL, NULL, 0, NULL}
};


#if (PY_MAJOR_VERSION == 2)
  PyMODINIT_FUNC
  initpuyocore(void)
  {
      PyObject *m;

      m = Py_InitModule("puyocore", PuyoMethods);
      if (m == NULL) {
          return;
        }
  }
#else
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
#endif
