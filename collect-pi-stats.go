package main
import (
    "golang.org/x/image/font"
    "golang.org/x/image/font/basicfont"
    "golang.org/x/image/math/fixed"
    "github.com/dustin/go-humanize"
    "image"
    "image/color"
    "image/png"
    "os"
    "fmt"
    "log"
    "math"
    "strings"
    "strconv"
    "time"
    "github.com/garyburd/redigo/redis" // the redis package is introduced
)

// Define a custom struct to hold pi data
type Pi struct {
	Hostname	string
	Temp		string
	Speed		string
	Hit		string
	Lastseen	int
	Outputinterval  int
	Processed	int
}

func main() {
    //now := time.Now()
    //secsnow := now.Unix()
    //Write and read data to redis through go
    //1. Link to redis
    conn, err := redis.Dial("tcp", "pistats:6379", '****')
    if err != nil {
        fmt.Println("redis.Dial err=", err)
        return 
    }
    defer conn.Close() // close

    total := int(0)

    img := image.NewRGBA(image.Rect(0, 0, 240, 320))
    // by default BG is white - change to black
    // white made the text really pop!!!
    //white := color.RGBA{255, 255, 255, 0xff}
    black := color.RGBA{0, 0, 0, 0xff}
    	for x := 0; x < 240; x++ {
		for y := 0; y < 320; y++ {
			img.Set(x, y, black)
		}
	}
    //red := color.RGBA{255, 0, 0, 0xff}
    green := color.RGBA{0, 255, 0, 0xff}
    //white := color.RGBA{255, 255, 255, 0xff}
    //yellow := color.RGBA{255, 227, 66, 0xff}
    gray := color.RGBA{127, 127, 127, 0xff}

    // get the pies
    keys, err := redis.Strings(conn.Do("keys", "pi*"))
    if err != nil {
      log.Fatal(err)
    }
    xi := 2
    y_line_width := 14
    for _, key := range keys {
        reply, err := redis.StringMap(conn.Do("HGETALL", key))
        if err != nil {
            log.Fatal(err)
        }
	if reply != nil {
		pi, err := populatePi(key, reply)
		if err != nil {
		    log.Fatal(err)
		}
		text := fmt.Sprint(key, ": ", pi.Temp, " @", pi.Speed, " ", humanize.Comma(int64(pi.Processed)), "/1m ", pi.Lastseen, "/s")
		fmt.Println(text)
		cT, err := strconv.ParseFloat(pi.Temp, 8)
		convTemp2 := fmt.Sprint(math.Round(cT))
		cTI, err := strconv.Atoi(convTemp2)
		tempColorR, tempColorG, tempColorB, err := colorByTemp(cTI)
    		custom := color.RGBA{uint8(tempColorR), uint8(tempColorG), uint8(tempColorB), 0xff}
		total = total + pi.Processed

		//find row for display based on hostname
		split := strings.Split(key, "i")
		hostnum, _ := strconv.Atoi(split[1])
		//fmt.Printf(key, hostnum, y_line_width)
		y_position := y_line_width * hostnum

		findit := "yes"
		if strings.Contains(pi.Hit, findit) {
			addLabel(img, xi, y_position, string(text), green)
		} else {
			if pi.Lastseen > 120 {
				addLabel(img, xi, y_position, string(text), gray)
			} else {
				addLabel(img, xi, y_position, string(text), custom)
			}
		}
		//xi = xi+10
		//yi = yi+14
	}
    }
    totalOut := fmt.Sprintf("Total: [%+v]", humanize.Comma(int64(total)))
    fmt.Println(totalOut)
    addLabel(img, 65, 305, totalOut, gray)
    //last, err := redis.String(conn.Do("GET", "lastupdate"))
    if err != nil {
        log.Println(err)
    }
    addLabel(img, 2, 318, "Last Updated:", gray)
    //addLabel(img, 0, 320, string(last), yellow)
    timeN := time.Now()
    addLabel(img, 100, 318, timeN.Format(time.Stamp), gray)

    f, err := os.Create("pi-stats-2.png")
    if err != nil {
        panic(err)
    }
    defer f.Close()
    if err := png.Encode(f, img); err != nil {
        panic(err)
    }
}

func populatePi(hostn string, reply map[string]string) (*Pi, error) {
	var err error
	now := time.Now()
	secsnow := now.Unix()
	pi := new(Pi)
	pi.Hostname = hostn
	pi.Temp = reply["temp"]
	pi.Speed = reply["speed"]
	pi.Hit = reply["hit"]
	//pi.Lastseen = reply["last"]
	//pi.OutputInterval = reply["outputinterval"]
	//pi.Processed = reply["processed"]
	lastseen, err := strconv.Atoi(reply["last"])
	if err != nil {
        	fmt.Println("10 err=", err)
		pi.Lastseen = 99999
		pi.Outputinterval = 0
		pi.Processed = 0
		//return nil, err
	} else {
		pi.Lastseen = int(secsnow) - lastseen
		pi.Outputinterval, err = strconv.Atoi(reply["outputInterval"])
		if err != nil {
			fmt.Println("11 err=", err)
			return nil, err
		}
		pi.Processed, err = strconv.Atoi(reply["processed"])
		if err != nil {
			fmt.Println("12 err=", err)
			return nil, err
		}
	}
	return pi, nil
}

func addLabel(img *image.RGBA, x, y int, label string, c color.RGBA) {
    //col := color.RGBA{200, 100, 0, 255}
    point := fixed.Point26_6{fixed.Int26_6(x * 64), fixed.Int26_6(y * 64)}

    d := &font.Drawer{
        Dst:  img,
        //Src:  image.NewUniform(col),
        Src:  image.NewUniform(c),
        Face: basicfont.Face7x13,
        Dot:  point,
    }
    d.DrawString(label)
}

func colorByTemp(temp int) (int, int, int, error) {
	r := 255
	g := 0
	b := 0
	steps := 21
	loops := 1
	//fmt.Println(temp)
	if temp > 80 {
		return r, g, b, nil
	}
	if temp > 75 {
		return r-(steps), g, b+(steps), nil
	}
	if temp > 70 {
		loops = 2
		return r-(steps*loops), g, b+(steps*loops), nil
	}
	if temp > 65 {
		loops = 3
		return r-(steps*loops), g, b+(steps*loops), nil
	}
	if temp > 60 {
		loops = 4
		return r-(steps*loops), g, b+(steps*loops), nil
	}
	if temp > 55 {
		loops = 5
		return r-(steps*loops), g, b+(steps*loops), nil
	}
	if temp > 50 {
		loops = 6
		return r-(steps*loops), g, b+(steps*loops), nil
	}
	if temp > 45 {
		loops = 7
		return r-(steps*loops), g, b+(steps*loops), nil
	}
	if temp > 40 {
		loops = 8
		return r-(steps*loops), g, b+(steps*loops), nil
	}
	if temp > 35 {
		loops = 9
		return r-(steps*loops), g, b+(steps*loops), nil
	} else {
		return 0, 0, 255, nil
	}
}

