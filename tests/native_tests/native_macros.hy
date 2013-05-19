(defmacro rev [&rest body]
  "Execute the `body` statements in reverse"
  (quasiquote (do (unquote-splice (list (reversed body))))))


(defn test-rev-macro []
  "NATIVE: test stararged native macros"
  (setv x [])
  (rev (.append x 1) (.append x 2) (.append x 3))
  (assert (= x [3 2 1])))

(defmacro finally [expr]
  (quasiquote (else (unquote expr))))

(defn test-try-expansion []
  "NATIVE: test macro expansion in (try ...) with expect macro"
  (setv result 0)
  (try
   (raise Exception)
   (except)
   (finally (setv result 1)))
  (assert (= result 1)))
