rooms = JSON.parse(rooms);
user_bookings = JSON.parse(user_bookings);
other_bookings = JSON.parse(other_bookings);
    
var out = "";
var i, x, z;
var cell_count = 0;
    
console.log(rooms);
console.log(user_bookings);
console.log(other_bookings);
    
var current_room;
var current_booking;

var time_match = false;

function empty_cell_func(roomID, buildingID, date_str, timeslot)
{
    out = "";
    out = out + '<td class="empty_cell" >';
    out = out + '<form class="empty_cell_form" method="post">';

    out = out + '<input type="hidden" name="csrfmiddlewaretoken" value="';
    out = out + CSRF_TOKEN;
    out = out + '">';

    out = out + '<input name="roomID" type="hidden" value="';
    out = out + roomID;
    out = out + '">';

    out = out + '<input name="date" type="hidden" value="';
    out = out + date_str;
    out = out + '">';

    out = out + '<input name="building" type="hidden" value="';
    out = out + buildingID;
    out = out + '">';

    out = out + '<input name="time" type="hidden" value="';
    out = out + timeslot;
    out = out + '">';

    out = out + '<input type="submit" name="empty_cell_submit" value=" " class="empty_submit">';

    out = out + '</form></td>';

    return out;
}

function user_cell_func(bookingID)
{
    out = "";
    out = out + '<td class="user_cell" onclick="location.href=\'/roombooking/viewbooking/';
    out = out + bookingID.toString();
    out = out + '\'">';
    out = out + '<a href="/roombooking/viewbooking/';
    out = out + bookingID.toString();
    out = out + '" class="blockbtn" > </a>';
    out = out + "</td>";

    return out
}
            
for(i = 0; i < rooms.length; i++) // Room Loop
{
    console.log(rooms[i].fields.name);
    current_room = rooms[i].pk;

    out = out + '<tr class="table_content_row"><td class="firstcol">'
    out = out + rooms[i].fields.name
    out = out + '</td>'
                
    for(x=0; x<=20; x++) // Time Loop
    {
        console.log("CURRENT TIME: " + x);
        time_match = false;
    
        for(z=0; z<other_bookings.length; z++) // Booking Loop
        {
            console.log("CURRENT BOOKING: " + z);
            if(other_bookings[z].fields.room == current_room) // Check Room
            {
                if(x == other_bookings[z].fields.startTime) // Check Time
                {
                    console.log("Found")
                    time_match = true;
                    current_booking = other_bookings[z]
    
                    console.log("Booking len: " + current_booking.fields.length)
    
                    for(var y=0; y<current_booking.fields.length; y++)
                    {
                    // Add content to out
                        console.log("ADDED TAKEN CELL");
                        out = out + '<td class="taken_cell"></td>';
                        cell_count++;
                    }
                            
                    //console.log("x b4: " + x);
                    x = x + other_bookings[z].fields.length - 1;
                    //console.log("x af: " + x);
                    console.log("BREAKING");
                    break;
                }
            }
        }

        for(var f = 0; f < user_bookings.length; f++)
        {
            console.log("CURRENT USER BOOKING: " + f);
            if(user_bookings[f].fields.room == current_room)
            {
                if(x == user_bookings[f].fields.startTime)
                {
                    console.log("User Found");
                    time_match = true;

                    current_booking = user_bookings[f];

                    for(var y = 0; y < current_booking.fields.length; y++)
                    {
                        console.log("ADDED USER CELL");
                        //out = out + '<td class="user_cell"></td>';

                        out = out + user_cell_func(current_booking.pk);

                        cell_count++;
                    }
                    x = x + user_bookings[f].fields.length - 1;
                    console.log("BREAKING");
                    break;
                }
            }
        }

        if(time_match == false)
        {
            console.log("ADDED EMPTY CELL");

            out = out + empty_cell_func(current_room.toString(), building_id, date, x)

            cell_count++;
        }

    }
    out = out + '</tr>';
    console.log(cell_count);
    console.log("Current out: " + out);
    
}
console.log("Out string final: " + out);
document.getElementById("table_contents").innerHTML = out;