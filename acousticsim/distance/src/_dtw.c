
#include <Python.h>
#include <numpy/arrayobject.h>

double dynamic_time_warping(PyArrayObject *arr)

{
    void* prevptr;
    void* curptr;
    double current;
    npy_intp distmat_size[2];
    npy_intp distmat_size[0] = PyArray_DIM(arr,0);
    npy_intp distmat_size[1] = PyArray_DIM(arr,1);

    for (i = 1; i < distmat_size[0]; ++i){
        prevptr = PyArray_GETPTR2(arr,i-1,0);
        curptr = PyArray_GETPTR2(arr,i,0);
        current = PyArray_GETITEM(arr,curptr);
        current += PyArray_GETITEM(arr,prevptr);
        if (PyArray_SETITEM(arr,curptr,current) == 0){
            DOSOMETHING?
        }
    }

    for (j = 1; j < distmat_size[1]; ++j){
        prevptr = PyArray_GETPTR2(arr,0,j-1);
        curptr = PyArray_GETPTR2(arr,0,j);
        current = PyArray_GETITEM(arr,curptr);
        current += PyArray_GETITEM(arr,prevptr);
        if (PyArray_SETITEM(arr,curptr,current) == 0){
            DOSOMETHING?
        }
    }

    double min;
    for (i = 1; i < distmat_size[0]; ++i){
        for (j = 1; j < distmat_size[1]; ++j){
            min = 10000.0;
            prevptr = PyArray_GETPTR2(arr,i-1,j-1);
            prev = PyArray_GETITEM(arr,prevptr);
            if (prev < min){
                min = prev;
            }
            prevptr = PyArray_GETPTR2(arr,i,j-1);
            prev = PyArray_GETITEM(arr,prevptr);
            if (prev < min){
                min = prev;
            }
            prevptr = PyArray_GETPTR2(arr,i-1,j);
            prev = PyArray_GETITEM(arr,prevptr);
            if (prev < min){
                min = prev;
            }


            curptr = PyArray_GETPTR2(arr,i,j);
            current = PyArray_GETITEM(arr,curptr);
            current += min;
            if (PyArray_SETITEM(arr,curptr,current) == 0){
                DOSOMETHING?
            }

        }
    }

    curptr = PyArray_GETPTR2(arr,distmat_size[0]-1,distmat_size[1]-1);
    current = PyArray_GETITEM(arr,curptr);
    current = current / (distmat_size[0]+distmat_size[1]);

    return current;

}


PyObject* PyArray_DTW(PyObject* self, PyObject* args)
{
    long order;
    PyObject *in = NULL;
    PyObject *out = NULL;
    if (!PyArg_ParseTuple(args, "Ol", &in)) {
        return NULL;
    }
    out = dynamic_time_warping(in);
    if (out == NULL) {
        if (!PyErr_ExceptionMatches(PyExc_ValueError)) {
            return NULL;
        }
    }
    return out;
}

static PyMethodDef dtwmethods[] = {
    {"dtw", PyArray_DTW, METH_VARARGS, NULL}
};

PyMODINIT_FUNC init_lpc(void)
{
    Py_InitModule("_dtw", dtwmethods);
    import_array();
}
