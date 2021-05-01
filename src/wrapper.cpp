#include "convert_funcs.hpp"
#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(convert_funcs, m) {
    m.doc() = R"pbdoc(Plugin to convert USPTO bulk patent data (from 1976 - present) to CSV from 
    TXT (original format).
    )pbdoc";

    m.def("txt_to_df", &txt_to_df_cpp, R"pbdoc(
    Function that takes USPTO (1976-2001) data from txt file, extracts pertinent fields, 
    and creates (or appends to) CSV output.

    Args: 
        input_file:  `string`, path of '.txt' file to read data from
        output_file: `string`, path of '.csv' file to store data
        append:  `bool`, open and writes to output_file in append mode if ``true``
        header: `bool`, prints header as first line to csv output_file if ``true``
    
    Returns:
        `int` -- number of patents read from TXT file
    )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}