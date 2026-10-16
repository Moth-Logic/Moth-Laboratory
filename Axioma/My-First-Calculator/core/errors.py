"""
errors.py
---------
Excepciones del core.

CalculatorError es la clase base de TODOS los errores que la calculadora
puede lanzar. Los errores específicos (LexerError, ParserError,
EvaluationError) viven en sus respectivos módulos pero heredan de esta
clase, por lo que un cliente puede capturar todo con un solo except:

    try:
        Calculator().evaluate(expr)
    except CalculatorError as exc:
        mostrar_error(str(exc))
"""


class CalculatorError(Exception):
    """Base class for every error raised by the calculation pipeline.

    Catching this single class is enough to handle any invalid input:
    LexerError, ParserError and EvaluationError all subclass it.
    """
