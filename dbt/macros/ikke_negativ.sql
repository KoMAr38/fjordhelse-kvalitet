{% test ikke_negativ(model, column_name) %}
-- Egendefinert generisk test. En andel kan ikke være negativ; slår den ut,
-- er det telleren eller nevneren som er feil, ikke visualiseringen.
select {{ column_name }}
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
