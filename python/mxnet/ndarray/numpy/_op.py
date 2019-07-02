# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Namespace for numpy operators used in Gluon dispatched by F=ndarray."""

from __future__ import absolute_import
import numpy as _np
from ...base import numeric_types
from ...util import _sanity_check_params, set_module
from ...context import current_context
from . import _internal as _npi
from ..ndarray import NDArray

__all__ = ['zeros', 'ones', 'maximum', 'minimum', 'stack', 'arange', 'argmax',
           'add', 'subtract', 'multiply', 'divide', 'mod', 'power', 'concatenate',
           'clip', 'split', 'swapaxes', 'expand_dims', 'tile', 'linspace',
           'sin', 'cos', 'sinh', 'cosh', 'log10', 'sqrt', 'arctanh', 'tan', 'fix', 'negative']

@set_module('mxnet.ndarray.numpy')
def zeros(shape, dtype=_np.float32, **kwargs):
    """Return a new array of given shape and type, filled with zeros.
    This function currently only supports storing multi-dimensional data
    in row-major (C-style).

    Parameters
    ----------
    shape : int or tuple of int
        The shape of the empty array.
    dtype : str or numpy.dtype, optional
        An optional value type. Default is `numpy.float32`. Note that this
        behavior is different from NumPy's `ones` function where `float64`
        is the default value, because `float32` is considered as the default
        data type in deep learning.
    ctx : Context, optional
        An optional device context (default is the current default context).

    Returns
    -------
    out : ndarray
        Array of zeros with the given shape, dtype, and ctx.
    """
    _sanity_check_params('zeros', ['order'], kwargs)
    ctx = kwargs.pop('ctx', current_context())
    if ctx is None:
        ctx = current_context()
    dtype = _np.float32 if dtype is None else dtype
    return _npi.zeros(shape=shape, ctx=ctx, dtype=dtype, **kwargs)


@set_module('mxnet.ndarray.numpy')
def ones(shape, dtype=None, **kwargs):
    """Return a new array of given shape and type, filled with ones.
    This function currently only supports storing multi-dimensional data
    in row-major (C-style).

    Parameters
    ----------
    shape : int or tuple of int
        The shape of the empty array.
    dtype : str or numpy.dtype, optional
        An optional value type. Default is `numpy.float32`. Note that this
        behavior is different from NumPy's `ones` function where `float64`
        is the default value, because `float32` is considered as the default
        data type in deep learning.
    ctx : Context, optional
        An optional device context (default is the current default context).

    Returns
    -------
    out : ndarray
        Array of zeros with the given shape, dtype, and ctx.
    """
    _sanity_check_params('zeros', ['order'], kwargs)
    ctx = kwargs.pop('ctx', current_context())
    if ctx is None:
        ctx = current_context()
    dtype = _np.float32 if dtype is None else dtype
    return _npi.ones(shape=shape, ctx=ctx, dtype=dtype, **kwargs)


#pylint: disable= too-many-arguments, no-member, protected-access
def _ufunc_helper(lhs, rhs, fn_array, fn_scalar, lfn_scalar, rfn_scalar=None, out=None):
    """ Helper function for element-wise operation.
    The function will perform numpy-like broadcasting if needed and call different functions.

    Parameters
    --------
    lhs : ndarray or numeric value
        Left-hand side operand.

    rhs : ndarray or numeric value
        Right-hand operand,

    fn_array : function
        Function to be called if both lhs and rhs are of ``ndarray`` type.

    fn_scalar : function
        Function to be called if both lhs and rhs are numeric values.

    lfn_scalar : function
        Function to be called if lhs is ``ndarray`` while rhs is numeric value

    rfn_scalar : function
        Function to be called if lhs is numeric value while rhs is ``ndarray``;
        if none is provided, then the function is commutative, so rfn_scalar is equal to lfn_scalar

    Returns
    --------
    mxnet.numpy.ndarray or scalar
        result array or scalar
    """
    from ...numpy import ndarray
    if isinstance(lhs, numeric_types):
        if isinstance(rhs, numeric_types):
            return fn_scalar(lhs, rhs, out=out)
        else:
            if rfn_scalar is None:
                # commutative function
                return lfn_scalar(rhs, float(lhs), out=out)
            else:
                return rfn_scalar(rhs, float(lhs), out=out)
    elif isinstance(rhs, numeric_types):
        return lfn_scalar(lhs, float(rhs), out=out)
    elif isinstance(rhs, ndarray):
        return fn_array(lhs, rhs, out=out)
    else:
        raise TypeError('type {} not supported'.format(str(type(rhs))))
#pylint: enable= too-many-arguments, no-member, protected-access


@set_module('mxnet.ndarray.numpy')
def maximum(x1, x2, out=None):
    """Returns element-wise maximum of the input arrays with broadcasting.

    Parameters
    ----------
    x1, x2 : scalar or mxnet.numpy.ndarray
        The arrays holding the elements to be compared. They must have the same shape,
        or shapes that can be broadcast to a single shape.

    Returns
    -------
    out : mxnet.numpy.ndarray or scalar
        The maximum of x1 and x2, element-wise. This is a scalar if both x1 and x2 are scalars."""
    return _ufunc_helper(x1, x2, _npi.maximum, _np.maximum, _npi.maximum_scalar, None, out)


@set_module('mxnet.ndarray.numpy')
def minimum(x1, x2, out=None):
    """Returns element-wise minimum of the input arrays with broadcasting.

    Parameters
    ----------
    x1, x2 : scalar or mxnet.numpy.ndarray
        The arrays holding the elements to be compared. They must have the same shape,
        or shapes that can be broadcast to a single shape.

    Returns
    -------
    out : mxnet.numpy.ndarray or scalar
        The minimum of x1 and x2, element-wise. This is a scalar if both x1 and x2 are scalars."""
    return _ufunc_helper(x1, x2, _npi.minimum, _np.minimum, _npi.minimum_scalar, None, out)


@set_module('mxnet.ndarray.numpy')
def stack(arrays, axis=0, out=None):
    """Join a sequence of arrays along a new axis.

        The axis parameter specifies the index of the new axis in the dimensions of the result.
        For example, if `axis=0` it will be the first dimension and if `axis=-1` it will be the last dimension.

    Parameters
    ----------
    arrays : sequence of array_like
        Each array must have the same shape.
    axis : int, optional
        The axis in the result array along which the input arrays are stacked.
    out : ndarray, optional
        If provided, the destination to place the result. The shape must be correct,
        matching that of what stack would have returned if no out argument were specified.

    Returns
    -------
    stacked : ndarray
        The stacked array has one more dimension than the input arrays."""
    def get_list(arrays):
        if not hasattr(arrays, '__getitem__') and hasattr(arrays, '__iter__'):
            raise ValueError("expected iterable for arrays but got {}".format(type(arrays)))
        return [arr for arr in arrays]

    arrays = get_list(arrays)
    return _npi.stack(*arrays, axis=axis, out=out)


@set_module('mxnet.ndarray.numpy')
def arange(start, stop=None, step=1, dtype=None, ctx=None):
    """Return evenly spaced values within a given interval.

    Values are generated within the half-open interval ``[start, stop)``
    (in other words, the interval including `start` but excluding `stop`).
    For integer arguments the function is equivalent to the Python built-in
    `range` function, but returns an ndarray rather than a list.

    Parameters
    ----------
    start : number, optional
        Start of interval. The interval includes this value.  The default
        start value is 0.
    stop : number
        End of interval. The interval does not include this value, except
        in some cases where `step` is not an integer and floating point
        round-off affects the length of `out`.
    step : number, optional
        Spacing between values. For any output `out`, this is the distance
        between two adjacent values, ``out[i+1] - out[i]``.  The default
        step size is 1.  If `step` is specified as a position argument,
        `start` must also be given.
    dtype : dtype
        The type of the output array. The default is `float32`.

    Returns
    -------
    arange : ndarray
        Array of evenly spaced values.

        For floating point arguments, the length of the result is
        ``ceil((stop - start)/step)``.  Because of floating point overflow,
        this rule may result in the last element of `out` being greater
        than `stop`.
    """
    if dtype is None:
        dtype = 'float32'
    if ctx is None:
        ctx = current_context()
    if stop is None:
        stop = start
        start = 0
    if step is None:
        step = 1
    if start is None and stop is None:
        raise ValueError('start and stop cannot be both None')
    if step == 0:
        raise ZeroDivisionError('step cannot be 0')
    return _npi.arange(start=start, stop=stop, step=step, dtype=dtype, ctx=ctx)


@set_module('mxnet.ndarray.numpy')
def argmax(a, axis=None, out=None):
    """Returns the indices of the maximum values along an axis.

    Parameters
    ----------
    a : ndarray
        Input array. Only support ndarrays of dtype `float16`, `float32`, and `float64`.
    axis : int, optional
        By default, the index is into the flattened array, otherwise
        along the specified axis.
    out : array, optional
        If provided, the result will be inserted into this array. It should
        be of the appropriate shape and dtype.

    Returns
    -------
    index_array : ndarray of indices whose dtype is same as the input ndarray.
        Array of indices into the array. It has the same shape as `a.shape`
        with the dimension along `axis` removed.
    """
    return _npi.argmax(a, axis=axis, keepdims=False, out=out)


@set_module('mxnet.ndarray.numpy')
def concatenate(seq, axis=0, out=None):
    """Join a sequence of arrays along an existing axis.

    Parameters
    ----------
    a1, a2, ... : sequence of array_like
        The arrays must have the same shape, except in the dimension
        corresponding to `axis` (the first, by default).
    axis : int, optional
        The axis along which the arrays will be joined.  If axis is None,
        arrays are flattened before use.  Default is 0.
    out : ndarray, optional
        If provided, the destination to place the result. The shape must be
        correct, matching that of what concatenate would have returned if no
        out argument were specified.

    Returns
    -------
    res : ndarray
        The concatenated array.
    """
    return _npi.concatenate(*seq, dim=axis, out=out)


@set_module('mxnet.ndarray.numpy')
def add(x1, x2, out=None):
    """Add arguments element-wise.

    Parameters
    ----------
    x1, x2 : ndarrays or scalar values
        The arrays to be added. If x1.shape != x2.shape, they must be broadcastable to
        a common shape (which may be the shape of one or the other).

    out : ndarray
        A location into which the result is stored. If provided, it must have a shape
        that the inputs broadcast to. If not provided or None, a freshly-allocated array
        is returned.

    Returns
    -------
    add : ndarray or scalar
        The sum of x1 and x2, element-wise. This is a scalar if both x1 and x2 are scalars.
    """
    return _ufunc_helper(x1, x2, _npi.add, _np.add, _npi.add_scalar, None, out)


@set_module('mxnet.ndarray.numpy')
def subtract(x1, x2, out=None):
    """Subtract arguments element-wise.

    Parameters
    ----------
    x1, x2 : ndarrays or scalar values
        The arrays to be subtracted from each other. If x1.shape != x2.shape,
        they must be broadcastable to a common shape (which may be the shape
        of one or the other).

    out : ndarray
        A location into which the result is stored. If provided, it must have a shape
        that the inputs broadcast to. If not provided or None, a freshly-allocated array
        is returned.

    Returns
    -------
    subtract : ndarray or scalar
        The difference of x1 and x2, element-wise. This is a scalar if both x1 and x2 are scalars.
    """
    return _ufunc_helper(x1, x2, _npi.subtract, _np.subtract, _npi.subtract_scalar,
                         _npi.rsubtract_scalar, out)


@set_module('mxnet.ndarray.numpy')
def multiply(x1, x2, out=None):
    """Multiply arguments element-wise.

    Parameters
    ----------
    x1, x2 : ndarrays or scalar values
        The arrays to be multiplied. If x1.shape != x2.shape, they must be broadcastable to
        a common shape (which may be the shape of one or the other).

    out : ndarray
        A location into which the result is stored. If provided, it must have a shape
        that the inputs broadcast to. If not provided or None, a freshly-allocated array
        is returned.

    Returns
    -------
    out : ndarray or scalar
        The multiplication of x1 and x2, element-wise. This is a scalar if both x1 and x2
        are scalars.
    """
    return _ufunc_helper(x1, x2, _npi.multiply, _np.multiply, _npi.multiply_scalar, None, out)


@set_module('mxnet.ndarray.numpy')
def divide(x1, x2, out=None):

    """
    Returns a true division of the inputs, element-wise.
    Instead of the Python traditional ‘floor division’, 
    this returns a true division. True division adjusts 
    the output type to present the best answer, regardless 
    of input types.

    Parameters:	
    ----------
    x1 : array_like
         Dividend array.
    x2 : array_like
         Divisor array.
    out : ndarray, None, or tuple of ndarray and None, optional
          A location into which the result is stored. If provided, 
          it must have a shape that the inputs broadcast to. 
          If not provided or None, a freshly-allocated array is returned. 
          A tuple (possible only as a keyword argument) must have length equal to the number of outputs.
    where : array_like, optional
            Values of True indicate to calculate the ufunc at that position, 
            values of False indicate to leave the value in the output alone.

    Returns:	
    --------
    y : ndarray
    Result is scalar if both inputs are scalar, ndarray otherwise.

    Examples:

    >>> x = np.arange(5)
    >>> np.divide(x, 4)
    array([ 0.  ,  0.25,  0.5 ,  0.75,  1.  ], dtype=float32)
    """

    return _ufunc_helper(x1, x2, _npi.true_divide, _np.divide, _npi.true_divide_scalar,
                         _npi.rtrue_divide_scalar, out)


@set_module('mxnet.ndarray.numpy')
def mod(x1, x2, out=None):
    """Return element-wise remainder of division.

    Parameters
    ----------
    x1 : ndarray or scalar
        Dividend array.

    x2 : ndarray or scalar
        Divisor array.

    out : ndarray
        A location into which the result is stored. If provided, it must have a shape
        that the inputs broadcast to. If not provided or None, a freshly-allocated array
        is returned.

    Returns
    -------
    out : ndarray or scalar
        This is a scalar if both x1 and x2 are scalars.
    """
    return _ufunc_helper(x1, x2, _npi.mod, _np.mod, _npi.mod_scalar, _npi.rmod_scalar, out)


@set_module('mxnet.ndarray.numpy')
def power(x1, x2, out=None):
    """First array elements raised to powers from second array, element-wise.

    Parameters
    ----------
    x1 : ndarray or scalar
        The bases.

    x2 : ndarray or scalar
        The exponent.

    out : ndarray
        A location into which the result is stored. If provided, it must have a shape
        that the inputs broadcast to. If not provided or None, a freshly-allocated array
        is returned.

    Returns
    -------
    out : ndarray or scalar
        The bases in x1 raised to the exponents in x2.
        This is a scalar if both x1 and x2 are scalars.
    """
    return _ufunc_helper(x1, x2, _npi.power, _np.power, _npi.power_scalar, _npi.rpower_scalar, out)


@set_module('mxnet.ndarray.numpy')
def clip(a, a_min, a_max, out=None):
    """Clip (limit) the values in an array.

    Given an interval, values outside the interval are clipped to
    the interval edges.  For example, if an interval of ``[0, 1]``
    is specified, values smaller than 0 become 0, and values larger
    than 1 become 1.

    Parameters
    ----------
    a : ndarray
        Array containing elements to clip.
    a_min : scalar or `None`
        Minimum value. If `None`, clipping is not performed on lower
        interval edge. Not more than one of `a_min` and `a_max` may be
        `None`.
    a_max : scalar or `None`
        Maximum value. If `None`, clipping is not performed on upper
        interval edge. Not more than one of `a_min` and `a_max` may be
        `None`.
    out : ndarray, optional
        The results will be placed in this array. It may be the input
        array for in-place clipping.  `out` must be of the right shape
        to hold the output.

    Returns
    -------
    clipped_array : ndarray
        An array with the elements of `a`, but where values
        < `a_min` are replaced with `a_min`, and those > `a_max`
        with `a_max`.
    """
    if a_min is None and a_max is None:
        raise ValueError('array_clip: must set either max or min')
    if a_min is None:
        a_min = float('-inf')
    if a_max is None:
        a_max = float('inf')
    return _npi.clip(a, a_min, a_max, out=out)


@set_module('mxnet.ndarray.numpy')
def swapaxes(a, axis1, axis2):
    """Interchange two axes of an array.

    Parameters:	
    -----------
    a : ndarray 
        Input array.
    axis1 : int
        First axis.
    axis2 : int
        Second axis.

    Returns:	
    -------
    a_swapped : ndarray

    Examples:
    >>> x = np.array([[1,2,3]])
    >>> np.swapaxes(x,0,1)
    array([[1.],
           [2.],
           [3.]])     
    """

    return _npi.swapaxes(a, dim1=axis1, dim2=axis2)


@set_module('mxnet.ndarray.numpy')
def expand_dims(a, axis):
    """Expand the shape of an array.

    Insert a new axis that will appear at the `axis` position in the expanded

    Parameters
    ----------
    a : ndarray
        Input array.
    axis : int
        Position in the expanded axes where the new axis is placed.

    Returns
    -------
    res : ndarray
        Output array. The number of dimensions is one greater than that of
        the input array.
    """
    return _npi.expand_dims(a, axis)


@set_module('mxnet.ndarray.numpy')
def split(ary, indices_or_sections, axis=0):
    """Split an array into multiple sub-arrays.

    Parameters
    ----------
    ary : ndarray
        Array to be divided into sub-arrays.
    indices_or_sections : int or 1-D array
        If `indices_or_sections` is an integer, N, the array will be divided
        into N equal arrays along `axis`.  If such a split is not possible,
        an error is raised.

        If `indices_or_sections` is a 1-D array of sorted integers, the entries
        indicate where along `axis` the array is split.  For example,
        ``[2, 3]`` would, for ``axis=0``, result in

          - ary[:2]
          - ary[2:3]
          - ary[3:]

        If an index exceeds the dimension of the array along `axis`,
        an empty sub-array is returned correspondingly.
    axis : int, optional
        The axis along which to split, default is 0.

    Returns
    -------
    sub-arrays : list of ndarrays
        A list of sub-arrays.

    Raises
    ------
    ValueError
        If `indices_or_sections` is given as an integer, but
        a split does not result in equal division.
    """
    indices = []
    axis_size = ary.shape[axis]
    if isinstance(indices_or_sections, int):
        sections = indices_or_sections
        if axis_size % sections:
            raise ValueError('array split does not result in an equal division')
        section_size = int(axis_size / sections)
        indices = [i * section_size for i in range(sections)]
    elif isinstance(indices_or_sections, tuple):
        indices = [0] + list(indices_or_sections)
    else:
        raise ValueError('indices_or_sections must either int or tuple of ints')
    ret = _npi.split(ary, indices, axis, False)
    if not isinstance(ret, list):
        raise NotImplementedError('single output from split is not supported yet...')
    return ret


@set_module('mxnet.ndarray.numpy')
def tile(A, reps):
    """
    Construct an array by repeating A the number of times given by reps.

    If `reps` has length ``d``, the result will have dimension of
    ``max(d, A.ndim)``.

    If ``A.ndim < d``, `A` is promoted to be d-dimensional by prepending new
    axes. So a shape (3,) array is promoted to (1, 3) for 2-D replication,
    or shape (1, 1, 3) for 3-D replication. If this is not the desired
    behavior, promote `A` to d-dimensions manually before calling this
    function.

    If ``A.ndim > d``, `reps` is promoted to `A`.ndim by pre-pending 1's to it.
    Thus for an `A` of shape (2, 3, 4, 5), a `reps` of (2, 2) is treated as
    (1, 1, 2, 2).

    Note : Although tile may be used for broadcasting, it is strongly
    recommended to use numpy's broadcasting operations and functions.

    Parameters
    ----------
    A : ndarray
        The input array.
    reps : tuple of integers
        The number of repetitions of `A` along each axis.

    Returns
    -------
    c : ndarray
        The tiled output array.
    """
    return _npi.tile(A, reps)


@set_module('mxnet.ndarray.numpy')
def linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None, axis=0, **kwargs):  # pylint: disable=too-many-arguments
    """Return evenly spaced numbers over a specified interval.

    Returns num evenly spaced samples, calculated over the interval [start, stop].
    The endpoint of the interval can optionally be excluded.

    Parameters
    ----------
    start : array_like
        The starting value of the sequence.
    stop : array_like
        The end value of the sequence, unless endpoint is set to False. In
        that case, the sequence consists of all but the last of num + 1
        evenly spaced samples, so that stop is excluded. Note that the step
        size changes when endpoint is False.
    num : int, optional
        Number of samples to generate. Default is 50. Must be non-negative.
    endpoint : bool, optional
        If True, stop is the last sample. Otherwise, it is not included.
        Default is True.
    retstep : bool, optional
        If True, return (samples, step), where step is the spacing between samples.
    dtype : dtype, optional
        The type of the output array. If dtype is not given, infer the data
        type from the other input arguments.
    axis : int, optional
        The axis in the result to store the samples. Relevant only if start or
        stop are array-like. By default (0), the samples will be along a new
        axis inserted at the beginning. Use -1 to get an axis at the end.

    Returns
    -------
    samples : ndarray
        There are num equally spaced samples in the closed interval
        `[start, stop]` or the half-open interval `[start, stop)`
        (depending on whether endpoint is True or False).
    step : float, optional
        Only returned if retstep is True
        Size of spacing between samples.

    Notes
    -----
    This function currently does not support ``start`` and ``stop`` as ndarrays and
    axis could only be 0 now.
    """
    if isinstance(start, (list, _np.ndarray, NDArray)) or \
       isinstance(stop, (list, _np.ndarray, NDArray)):
        raise NotImplementedError('start and stop only support int')
    if axis != 0:
        raise NotImplementedError("the function only support axis 0")
    ctx = kwargs.pop('ctx', current_context())
    if ctx is None:
        ctx = current_context()
    if retstep:
        step = (stop - start) / (num - 1)
        return _npi.linspace(start=start, stop=stop, num=num, endpoint=endpoint, ctx=ctx, dtype=dtype), step
    else:
        return _npi.linspace(start=start, stop=stop, num=num, endpoint=endpoint, ctx=ctx, dtype=dtype)


def _unary_func_helper(x, fn_array, fn_scalar, out=None, **kwargs):
    """Helper function for unary operators.

    Parameters
    ----------
    x : ndarray or scalar
        Input of the unary operator.
    fn_array : function
        Function to be called if x is of ``ndarray`` type.
    fn_scalar : function
        Function to be called if x is a Python scalar.
    out : ndarray
        The buffer ndarray for storing the result of the unary function.

    Returns
    -------
    out : mxnet.numpy.ndarray or scalar
        Result array or scalar.
    """
    if isinstance(x, numeric_types):
        return fn_scalar(x, **kwargs)
    elif isinstance(x, NDArray):
        return fn_array(x, out=out, **kwargs)
    else:
        raise TypeError('type {} not supported'.format(str(type(x))))


@set_module('mxnet.ndarray.numpy')
def sin(x, out=None, **kwargs):
    r"""Trigonometric sine, element-wise.

    Parameters
    ----------
    x : ndarray or scalar
        Angle, in radians (:math:`2 \pi` rad equals 360 degrees).
    out : ndarray or None
        A location into which the result is stored. If provided, it
        must have a shape that the inputs broadcast to. If not provided
        or None, a freshly-allocated array is returned. The dtype of the
        output is the same as that of the input if the input is an ndarray.

    Returns
    -------
    y : ndarray or scalar
        The sine of each element of x. This is a scalar if `x` is a scalar.

    Notes
    ----
    This function only supports input type of float.
    """
    return _unary_func_helper(x, _npi.sin, _np.sin, out=out, **kwargs)

@set_module('mxnet.ndarray.numpy')
def cos(x, out=None, **kwargs):
    r"""Cosine, element-wise.

    Parameters
    ----------
    x : ndarray or scalar
        Angle, in radians (:math:`2 \pi` rad equals 360 degrees).
    out : ndarray or None
        A location into which the result is stored. If provided, it
        must have a shape that the inputs broadcast to. If not provided
        or None, a freshly-allocated array is returned. The dtype of the
        output is the same as that of the input if the input is an ndarray.

    Returns
    -------
    y : ndarray or scalar
        The corresponding cosine values. This is a scalar if x is a scalar.

    Notes
    ----
    This function only supports input type of float.
    """
    return _unary_func_helper(x, _npi.cos, _np.cos, out=out, **kwargs)


@set_module('mxnet.ndarray.numpy')
def sinh(x, out=None, **kwargs):
    """Hyperbolic sine, element-wise.

    Equivalent to ``1/2 * (np.exp(x) - np.exp(-x))`` or ``-1j * np.sin(1j*x)``.

    Parameters
    ----------
    x : ndarray or scalar
        Input array or scalar.
    out : ndarray or None
        A location into which the result is stored. If provided, it
        must have a shape that the inputs broadcast to. If not provided
        or None, a freshly-allocated array is returned. The dtype of the
        output is the same as that of the input if the input is an ndarray.

    Returns
    -------
    y : ndarray or scalar
        The corresponding hyperbolic sine values. This is a scalar if `x` is a scalar.

    Notes
    ----
    This function only supports input type of float.
    """
    return _unary_func_helper(x, _npi.sinh, _np.sinh, out=out, **kwargs)


@set_module('mxnet.ndarray.numpy')
def cosh(x, out=None, **kwargs):
    """Hyperbolic cosine, element-wise.

    Equivalent to ``1/2 * (np.exp(x) + np.exp(-x))`` and ``np.cos(1j*x)``.


    Parameters
    ----------
    x : ndarray or scalar
        Input array or scalar.
    out : ndarray or None
        A location into which the result is stored. If provided, it
        must have a shape that the inputs broadcast to. If not provided
        or None, a freshly-allocated array is returned. The dtype of the
        output is the same as that of the input if the input is an ndarray.

    Returns
    -------
    y : ndarray or scalar
        The corresponding hyperbolic cosine values. This is a scalar if `x` is a scalar.

    Notes
    ----
    This function only supports input type of float.
    """
    return _unary_func_helper(x, _npi.cosh, _np.cosh, out=out, **kwargs)


@set_module('mxnet.ndarray.numpy')
def log10(x, out=None, **kwargs):
    """Return the base 10 logarithm of the input array, element-wise.

    Parameters
    ----------
    x : ndarray or scalar
        Input array or scalar.
    out : ndarray or None
        A location into which the result is stored. If provided, it
        must have a shape that the inputs broadcast to. If not provided
        or None, a freshly-allocated array is returned. The dtype of the
        output is the same as that of the input if the input is an ndarray.

    Returns
    -------
    y : ndarray or scalar
        The logarithm to the base 10 of `x`, element-wise. NaNs are
        returned where x is negative. This is a scalar if `x` is a scalar.

    Notes
    ----
    This function only supports input type of float.
    """
    return _unary_func_helper(x, _npi.log10, _np.log10, out=out, **kwargs)


@set_module('mxnet.ndarray.numpy')
def sqrt(x, out=None, **kwargs):
    r"""
    Return the non-negative square-root of an array, element-wise.

    Parameters
    ----------
    x : ndarray or scalar
        The values whose square-roots are required.
    out : ndarray, or None, optional
        A location into which the result is stored. If provided, it must have
        a shape that the inputs broadcast to. If not provided or `None`,
        a freshly-allocated array is returned.

    Returns
    -------
    y : ndarray or scalar
        An array of the same shape as `x`, containing the positive
        square-root of each element in `x`. This is a scalar if `x` is a scalar.

    Notes
    ----
    This function only supports input type of float.
    """
    return _unary_func_helper(x, _npi.sqrt, _np.sqrt, out=out, **kwargs)

@set_module('mxnet.ndarray.numpy')
def arctanh(x, out=None, where=True, **kwargs):
    r"""
    arctanh(x, out=None, where=True)

    Inverse hyperbolic tangent element-wise.

    Parameters:	

    -----------
    x : ndarray 
        Input array.
    out : ndarray, None.
          A location into which the result is stored. If provided, 
          it must have a shape that the inputs broadcast to. 
          If not provided or None, a freshly-allocated array is returned. 
          A tuple (possible only as a keyword argument) 
          must have length equal to the number of outputs.
    where : ndarray, optional
            Values of True indicate to calculate the ufunc at that position, 
            values of False indicate to leave the value in the output alone.
    Returns:	
    --------
    out : ndarray or scalar
          ndarray of the same shape as x. This is a scalar if x is a scalar.
    Examples

    >>> np.arctan(0.7)
    0.8673005276940531
    """

    return _unary_func_helper(x, _npi.arctanh, _np.arctanh, out=out, **kwargs)

@set_module('mxnet.ndarray.numpy')
def tan(x, out=None, where=True, **kwargs):
    r"""
    tan(x, out=None, where=True)

    Compute tangent element-wise.
    Equivalent to np.sin(x)/np.cos(x) element-wise.
    
    Parameters:	
    ----------
    x : array_like
        Input array.
    out : ndarray, None, or tuple of ndarray and None, optional
          A location into which the result is stored. If provided, 
          it must have a shape that the inputs broadcast to. If not provided or None, 
          a freshly-allocated array is returned. A tuple (possible only as a keyword argument) 
          must have length equal to the number of outputs.
    where : ndarray, optional
            Values of True indicate to calculate the ufunc at that position, 
            values of False indicate to leave the value in the output alone.

    Returns:	
    -------
    y : ndarray
    The corresponding tangent values. This is a scalar if x is a scalar.

    Examples:

    >>> np.tan(0.5)
    0.5463024898437905 
    """

    return _unary_func_helper(x, _npi.tan, _np.tan, out=out, **kwargs)

@set_module('mxnet.ndarray.numpy')
def fix(x, out=None):
    r"""
    Round an array of floats element-wise to nearest integer towards zero.
    The rounded values are returned as floats.
    
    Parameters:
    ----------
    x : ndarray
        An array of floats to be rounded
    out : ndarray, optional
        Output array

    Returns:
    -------
    y : ndarray of floats

    Examples
    --------- 
    >>> np.fix(3.14)
    3
    """
    return _unary_func_helper(x, _npi.fix, _np.fix, out=out)

@set_module('mxnet.ndarray.numpy')
def negative(x, out=None, where=True, **kwargs):
    r""" 
    negative(x, out=None, where=True)

    Numerical negative, element-wise.

    Parameters:	
    ------------
    x : ndarray or scalar
        Input array.
    out : ndarray, None, or tuple of ndarray and None, optional
          A location into which the result is stored. 
    where : ndarray, optional
            Values of True indicate to calculate the ufunc at that position, 
            values of False indicate to leave the value in the output alone.

    Returns: 
    ---------
    y : ndarray or scalar
        Returned array or scalar: y = -x. This is a scalar if x is a scalar.

    Examples:
    ---------
    >>> np.negative(1)
    -1
    """
    return _unary_func_helper(x, _npi.negative, _np.negative, out=out)
