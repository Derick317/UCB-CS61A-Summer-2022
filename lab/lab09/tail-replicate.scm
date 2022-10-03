(define (tail-replicate x n)
  ; BEGIN
  (define (help-replicate l n)
    (if (= n 0)
      l
      (help-replicate (cons x l) (- n 1))
    )
  )
  (help-replicate nil n)
  ; END
)