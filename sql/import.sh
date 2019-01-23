
ls -1 good/*.sql | while read line
do
echo $line
my < $line
done

