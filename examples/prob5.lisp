(defun mygcd (a b)
  (if (= b 0)
      a
      (mygcd b (% a b))))

(defun mylcm (a b)
  (/ (* a b) (mygcd a b)))

(defun range (n)
  (if (= n 1)
      1
      (mylcm n (range (- n 1)))))

(range 20)