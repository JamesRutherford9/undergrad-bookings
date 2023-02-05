var x = "<th>Room</th>", i;
for(i=8; i<=17; i++){
    x = x + "<th>" + i + ":00</th>";
    x = x + "<th>" + i + ":30</th>";
}
x = x + "<th>18:00</th>";

document.getElementById("room_date_table").innerHTML = x;