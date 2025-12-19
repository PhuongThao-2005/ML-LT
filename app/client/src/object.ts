import { type POIResponse } from "./types";

export const mock: POIResponse = {
    city: "ha noi",
    start_point: "Wyndham Garden Hanoi",
    days: 3,
    itinerary: [
        {
            day: 1,
            route: [
                {
                    poi_id: "hotel01843",
                    type: "Start",
                    name: "Wyndham Garden Hanoi",
                    arrival_time: "08:30",
                    travel_before_min: 0,
                    longitude: 105.771767,
                    latitude: 20.983948,
                    duration_min: 0,
                    order: 1,
                    address: "Yên Phụ, Quận Tây Hồ, Hà Nội, Vietnam",
                    rating: 4.3
                },
                {
                    poi_id: "attraction00637",
                    type: "Visit",
                    name: "Vietnamtour",
                    arrival_time: "08:37",
                    travel_before_min: 7,
                    longitude: 105.7920069,
                    latitude: 21.0241969,
                    duration_min: 97,
                    order: 2,
                    address: "32 Hàng Bài, Hoàn Kiếm, Hà Nội, Vietnam",
                    rating: 4.7
                },
                {
                    poi_id: "attraction00568",
                    type: "Visit",
                    name: "Hanoi Tour Guide - Hanoi Tours, Activities & Things to Do",
                    arrival_time: "10:16",
                    travel_before_min: 2,
                    longitude: 105.8001835,
                    latitude: 21.0196489,
                    duration_min: 97,
                    order: 3
                },
                {
                    poi_id: "restaurant01186",
                    type: "Lunch",
                    name: "Vị Quảng (Nhà hàng 13 năm tuổi)",
                    arrival_time: "11:54",
                    travel_before_min: 1,
                    duration_min: 90,
                    order: 4
                },
                {
                    poi_id: "attraction00655",
                    type: "Visit",
                    name: "The Hangout Tattoo Studio - Ha Noi",
                    arrival_time: "13:33",
                    travel_before_min: 9,
                    longitude: 105.859306,
                    latitude: 21.0283489,
                    duration_min: 97,
                    order: 5
                },
                {
                    poi_id: "attraction00620",
                    type: "Visit",
                    name: "Vietnam Motorcycle Tours | VietnamBikers",
                    arrival_time: "15:21",
                    travel_before_min: 11,
                    longitude: 105.7963062,
                    latitude: 20.987035,
                    duration_min: 97,
                    order: 6
                },
                {
                    poi_id: "restaurant01190",
                    type: "Dinner",
                    name: "Chum Korean Restaurant",
                    arrival_time: "16:58",
                    travel_before_min: 4,
                    duration_min: 90,
                    order: 7
                },
                {
                    poi_id: "hotel01843",
                    type: "Return Hotel",
                    name: "End of Day",
                    arrival_time: "18:33",
                    travel_before_min: 5,
                    duration_min: 0,
                    order: 8
                }
            ]
        },
        {
            day: 2,
            route: [
                {
                    poi_id: "hotel01843",
                    type: "Start",
                    name: "Wyndham Garden Hanoi",
                    arrival_time: "08:30",
                    travel_before_min: 0,
                    longitude: 105.771767,
                    latitude: 20.983948,
                    duration_min: 0,
                    order: 1
                },
                {
                    poi_id: "attraction00659",
                    type: "Visit",
                    name: "Peridot Spa (Grand)",
                    arrival_time: "08:41",
                    travel_before_min: 11,
                    longitude: 105.8464439,
                    latitude: 21.0333031,
                    duration_min: 97,
                    order: 2
                },
                {
                    poi_id: "attraction00643",
                    type: "Visit",
                    name: "TiredCity 54 Bát Sứ",
                    arrival_time: "10:18",
                    travel_before_min: 0,
                    longitude: 105.8472944,
                    latitude: 21.0344603,
                    duration_min: 97,
                    order: 3
                },
                {
                    poi_id: "attraction00643",
                    type: "Lunch",
                    name: "TiredCity 54 Bát Sứ",
                    arrival_time: "11:55",
                    travel_before_min: 0,
                    duration_min: 90,
                    order: 4
                },
                {
                    poi_id: "attraction00615",
                    type: "Visit",
                    name: "Crossing Vietnam Tour",
                    arrival_time: "13:25",
                    travel_before_min: 0,
                    longitude: 105.8480191,
                    latitude: 21.0354879,
                    duration_min: 97,
                    order: 5
                },
                {
                    poi_id: "attraction00613",
                    type: "Visit",
                    name: "Hanoi Backstreet Tours - Hanoi Jeep Tours - Hanoi Vespa Tours - Hanoi Motorbike Tours",
                    arrival_time: "15:04",
                    travel_before_min: 2,
                    longitude: 105.8550014,
                    latitude: 21.033617,
                    duration_min: 97,
                    order: 6
                },
                {
                    poi_id: "attraction00613",
                    type: "Dinner",
                    name: "Hanoi Backstreet Tours - Hanoi Jeep Tours - Hanoi Vespa Tours - Hanoi Motorbike Tours",
                    arrival_time: "16:41",
                    travel_before_min: 0,
                    duration_min: 90,
                    order: 7
                },
                {
                    poi_id: "hotel01843",
                    type: "Return Hotel",
                    name: "End of Day",
                    arrival_time: "18:25",
                    travel_before_min: 14,
                    duration_min: 0,
                    order: 8
                }
            ]
        }
    ]
}