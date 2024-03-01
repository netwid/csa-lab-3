(defun sum (a)
    (if (= a 1) 1 (+ a (sum (- a 1)))))

(sum 2)