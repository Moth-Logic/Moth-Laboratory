/**
 * evaluator.cpp
 * -------------
 * C++ implementation of the evaluator for performance-critical paths.
 * This module is compiled as a Python extension via pybind11.
 *
 * Same interface as the Python Evaluator: takes an AST (represented as
 * nested dictionaries) and returns a float result.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>
#include <stdexcept>
#include <string>
#include <variant>

namespace py = pybind11;

// ---------- Custom exception ------------------------------------------------

class EvaluationError : public std::runtime_error {
public:
    explicit EvaluationError(const std::string& msg) : std::runtime_error(msg) {}
};

// ---------- Mathematical helpers --------------------------------------------

static double deg_to_rad(double deg) {
    return deg * M_PI / 180.0;
}

static double rad_to_deg(double rad) {
    return rad * 180.0 / M_PI;
}

static double cbrt_signed(double x) {
    return std::copysign(std::pow(std::abs(x), 1.0 / 3.0), x);
}

// ---------- Operator application --------------------------------------------

static double apply_operator(const std::string& op, double left, double right) {
    if (op == "+") return left + right;
    if (op == "-") return left - right;
    if (op == "*") return left * right;
    if (op == "/") {
        if (right == 0.0) throw EvaluationError("División entre cero");
        return left / right;
    }
    if (op == "^") {
        try {
            return std::pow(left, right);
        } catch (const std::overflow_error&) {
            throw EvaluationError("Resultado demasiado grande");
        }
    }
    if (op == "%") {
        if (right == 0.0) throw EvaluationError("Módulo por cero");
        return std::fmod(left, right);
    }
    throw EvaluationError("Operador desconocido: " + op);
}

// ---------- Function application --------------------------------------------

static double apply_function(const std::string& name, double value) {
    // Trigonometric (degrees input)
    if (name == "sin") return std::sin(deg_to_rad(value));
    if (name == "cos") return std::cos(deg_to_rad(value));
    if (name == "tan") {
        double rad = deg_to_rad(value);
        if (std::cos(rad) == 0.0) throw EvaluationError("Tangente indefinida");
        return std::tan(rad);
    }
    if (name == "asin") {
        if (value < -1.0 || value > 1.0) throw EvaluationError("asin fuera de dominio");
        return rad_to_deg(std::asin(value));
    }
    if (name == "acos") {
        if (value < -1.0 || value > 1.0) throw EvaluationError("acos fuera de dominio");
        return rad_to_deg(std::acos(value));
    }
    if (name == "atan") return rad_to_deg(std::atan(value));

    // Hyperbolic
    if (name == "sinh") return std::sinh(value);
    if (name == "cosh") return std::cosh(value);
    if (name == "tanh") return std::tanh(value);

    // Power / root
    if (name == "sqrt") {
        if (value < 0.0) throw EvaluationError("Raíz cuadrada de número negativo");
        return std::sqrt(value);
    }
    if (name == "cbrt") return cbrt_signed(value);
    if (name == "exp") return std::exp(value);

    // Logarithms
    if (name == "log") {
        if (value <= 0.0) throw EvaluationError("Logaritmo de número no positivo");
        return std::log10(value);
    }
    if (name == "ln") {
        if (value <= 0.0) throw EvaluationError("Logaritmo de número no positivo");
        return std::log(value);
    }

    // Rounding
    if (name == "ceil") return std::ceil(value);
    if (name == "floor") return std::floor(value);
    if (name == "round") return std::round(value);

    // Other
    if (name == "abs") return std::abs(value);

    throw EvaluationError("Función desconocida: " + name);
}

// ---------- AST evaluator ---------------------------------------------------

static double evaluate_node(py::object node) {
    std::string node_type = node.attr("__class__").attr("__name__").cast<std::string>();

    if (node_type == "Number") {
        return node.attr("value").cast<double>();
    }

    if (node_type == "UnaryOp") {
        std::string op = node.attr("operator").attr("name").cast<std::string>();
        py::object operand = node.attr("operand");
        double value = evaluate_node(operand);
        return (op == "MINUS") ? -value : value;
    }

    if (node_type == "BinaryOp") {
        py::object left_node = node.attr("left");
        py::object right_node = node.attr("right");
        std::string op = node.attr("operator").attr("name").cast<std::string>();

        // Map TokenType names to operator strings
        std::string op_str;
        if (op == "PLUS") op_str = "+";
        else if (op == "MINUS") op_str = "-";
        else if (op == "STAR") op_str = "*";
        else if (op == "SLASH") op_str = "/";
        else if (op == "CARET") op_str = "^";
        else if (op == "PERCENT") op_str = "%";
        else throw EvaluationError("Operador desconocido: " + op);

        double left = evaluate_node(left_node);
        double right = evaluate_node(right_node);
        return apply_operator(op_str, left, right);
    }

    if (node_type == "FunctionCall") {
        std::string name = node.attr("name").cast<std::string>();
        py::object argument = node.attr("argument");
        double value = evaluate_node(argument);
        return apply_function(name, value);
    }

    throw EvaluationError("Nodo AST desconocido: " + node_type);
}

// ---------- Python-facing wrapper -------------------------------------------

static double cpp_evaluate(py::object node) {
    try {
        return evaluate_node(node);
    } catch (const EvaluationError& e) {
        throw py::value_error(e.what());
    }
}

// ---------- Module binding --------------------------------------------------

PYBIND11_MODULE(_evaluator_cpp, m) {
    m.doc() = "C++ evaluator backend for My First Calculator";

    m.def("evaluate", &cpp_evaluate,
          py::arg("node"),
          "Evaluate an AST node and return the float result.\n"
          "\n"
          "Args:\n"
          "    node: An AST node (Number, BinaryOp, UnaryOp, FunctionCall)\n"
          "\n"
          "Returns:\n"
          "    The computed float value.\n"
          "\n"
          "Raises:\n"
          "    ValueError: On division by zero, unknown operator, etc.");
}
