{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

Methods
~~~~~~~
.. rubric:: Layout generation methods

.. autosummary::
    :toctree: ./
    :nosignatures:

    ~Layout.__add__
    ~Layout.__or__


.. rubric:: Customization methods

.. autosummary::
    :toctree: ./
    :nosignatures:

    ~Layout.opts

.. rubric:: Output methods

.. autosummary::
    :toctree: ./
    :nosignatures:

    ~Layout.plot
    ~Layout.save
    ~Layout.show
