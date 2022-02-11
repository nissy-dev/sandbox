select
  t1.name as flavor1,
  t2.name as flavor2,
  (t1.calorie + t2.calorie) as total_calorie
from icecream as t1
inner join icecream as t2 on t1.name > t2.name;

select
  t1.name as flavor1,
  t2.name as flavor2,
  (t1.calorie + t2.calorie) as total_calorie
from icecream as t1
inner join icecream as t2 on t1.name > t2.name
where t1.calorie + t2.calorie <= 350 and (t1.kind = 'ELEGANT'  or t2.kind = 'ELEGANT' )
order by  total_calorie asc;

select name, kind, calorie
from icecream as t1
where calorie = (
  select min(t2.calorie)
  from icecream as t2 where t1.kind = t2.kind
)
order by kind = 'ELEGANT' desc, kind = 'THE 31' desc, kind asc;
